#!/bin/bash
###
# Claude Code Stop Hook - LangSmith Tracing Integration
# Sends Claude Code traces to LangSmith after each response.
###

set -e

# Config (needed early for logging)
# When CC_LANGSMITH_DEBUG=true, also write to /workspace so logs survive Docker --rm
DEBUG="$(echo "$CC_LANGSMITH_DEBUG" | tr '[:upper:]' '[:lower:]')"
if [ "$DEBUG" = "true" ]; then
    LOG_FILE="/workspace/_hook_debug.log"
else
    LOG_FILE="$HOME/.claude/state/hook.log"
fi

# Crash diagnostics (only when CC_LANGSMITH_DEBUG=true)
_hook_start_time=$(date +%s)
if [ "$DEBUG" = "true" ]; then
    trap 'echo "$(date +%Y-%m-%dT%H:%M:%S) ERR at line $LINENO (exit=$?)" >> /workspace/_hook_crash.log 2>/dev/null' ERR
    trap '_exit=$?; if [ $_exit -ne 0 ]; then echo "$(date +%Y-%m-%dT%H:%M:%S) EXIT code=$_exit elapsed=$(($(date +%s) - _hook_start_time))s" >> /workspace/_hook_crash.log 2>/dev/null; fi' EXIT
    echo "$(date +%Y-%m-%dT%H:%M:%S) HOOK_ALIVE pid=$$ ppid=$PPID" >> /workspace/_hook_crash.log 2>/dev/null
fi

# Logging functions
log() {
    local level="$1"
    shift
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $*" >> "$LOG_FILE"
}

debug() {
    if [ "$DEBUG" = "true" ]; then
        log "DEBUG" "$@"
    fi
}

# Immediate debug logging
debug "Hook started, TRACE_TO_LANGSMITH=$TRACE_TO_LANGSMITH"

# Exit early if tracing disabled
if [ "$(echo "$TRACE_TO_LANGSMITH" | tr '[:upper:]' '[:lower:]')" != "true" ]; then
    debug "Tracing disabled, exiting early"
    exit 0
fi

# Required commands
for cmd in jq curl uuidgen; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is required but not installed" >&2
        exit 0
    fi
done

# Config (continued)
API_KEY="${CC_LANGSMITH_API_KEY:-$LANGSMITH_API_KEY}"
PROJECT="${CC_LANGSMITH_PROJECT:-claude-code}"
API_BASE="${LANGSMITH_ENDPOINT:-https://api.smith.langchain.com}"
STATE_FILE="${STATE_FILE:-$HOME/.claude/state/langsmith_state.json}"

# Experiment trace context (nest CC traces under experiment run)
EXPERIMENT_TRACE_ID="${CC_LS_TRACE_ID:-}"
EXPERIMENT_RUN_ID="${CC_LS_PARENT_RUN_ID:-}"
EXPERIMENT_DOTTED_ORDER="${CC_LS_DOTTED_ORDER:-}"

# Global variables
CURRENT_TURN_ID=""  # Track current turn run for cleanup on exit
PARENT_RUN_ID=""    # Parent run that groups all turns
PARENT_DOTTED_ORDER=""  # dotted_order of the parent run

# Ensure state directory exists
mkdir -p "$(dirname "$STATE_FILE")"

# Validate API key
if [ -z "$API_KEY" ]; then
    log "ERROR" "CC_LANGSMITH_API_KEY not set"
    exit 0
fi

# Get microseconds portably (macOS doesn't support date +%N)
get_microseconds() {
    if command -v gdate &> /dev/null; then
        # Use GNU date if available (brew install coreutils)
        gdate +%6N
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS fallback: use Python for microseconds
        python3 -c "import time; print(str(int(time.time() * 1000000) % 1000000).zfill(6))"
    else
        # Linux/GNU date
        date +%6N
    fi
}

# Get file size portably (macOS and Linux have different stat syntax)
get_file_size() {
    local file="$1"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        stat -f%z "$file"
    else
        stat -c%s "$file"
    fi
}

# API call helper
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"

    local response
    local http_code
    response=$(curl -s --max-time 60 -w "\n%{http_code}" -X "$method" \
        -H "x-api-key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d "$data" \
        "$API_BASE$endpoint" 2>&1)

    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | sed '$d')

    if [ "$http_code" -lt 200 ] || [ "$http_code" -ge 300 ]; then
        log "ERROR" "API call failed: $method $endpoint"
        log "ERROR" "HTTP $http_code: $response"
        log "ERROR" "Request data: ${data:0:500}"
        return 1
    fi

    echo "$response"
}

# Cleanup function to complete pending turn run on exit
cleanup_pending_turn() {
    if [ -n "$CURRENT_TURN_ID" ]; then
        debug "Cleanup: completing pending turn run $CURRENT_TURN_ID"
        local now
        now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

        local turn_update
        turn_update=$(jq -n \
            --arg time "$now" \
            '{
                outputs: {messages: []},
                end_time: $time,
                error: "Incomplete: script exited early"
            }')

        # Try to complete the turn run (ignore errors since we're exiting anyway)
        api_call "PATCH" "/runs/$CURRENT_TURN_ID" "$turn_update" > /dev/null 2>&1 || true
        log "WARN" "Completed pending turn run $CURRENT_TURN_ID due to early exit"
    fi
}

# Set trap to cleanup on exit (EXIT covers normal exit, errors, and interrupts)
trap cleanup_pending_turn EXIT

# Load state
load_state() {
    if [ ! -f "$STATE_FILE" ]; then
        echo "{}"
        return
    fi
    cat "$STATE_FILE"
}

# Save state
save_state() {
    local state="$1"
    echo "$state" > "$STATE_FILE"
}

# Get message content
get_content() {
    local msg="$1"
    echo "$msg" | jq -c 'if type == "object" and has("message") then .message.content elif type == "object" then .content else null end'
}

# Check if message is tool result
is_tool_result() {
    local msg="$1"
    local content
    content=$(get_content "$msg")

    if echo "$content" | jq -e 'if type == "array" then any(.[]; type == "object" and .type == "tool_result") else false end' > /dev/null 2>&1; then
        echo "true"
    else
        echo "false"
    fi
}

# Format content blocks for LangSmith
format_content() {
    local msg="$1"
    local content
    content=$(get_content "$msg")

    # Handle string content
    if echo "$content" | jq -e 'type == "string"' > /dev/null 2>&1; then
        echo "$content" | jq '[{"type": "text", "text": .}]'
        return
    fi

    # Handle array content
    if echo "$content" | jq -e 'type == "array"' > /dev/null 2>&1; then
        echo "$content" | jq '[
            .[] |
            if type == "object" then
                if .type == "text" then
                    {"type": "text", "text": .text}
                elif .type == "thinking" then
                    {"type": "thinking", "thinking": .thinking}
                elif .type == "tool_use" then
                    {"type": "tool_call", "name": .name, "args": .input, "id": .id}
                else
                    .
                end
            elif type == "string" then
                {"type": "text", "text": .}
            else
                .
            end
        ] | if length == 0 then [{"type": "text", "text": ""}] else . end'
        return
    fi

    # Default
    echo '[{"type": "text", "text": ""}]'
}

# Get tool uses from message
get_tool_uses() {
    local msg="$1"
    local content
    content=$(get_content "$msg")

    # Check if content is an array
    if ! echo "$content" | jq -e 'type == "array"' > /dev/null 2>&1; then
        echo "[]"
        return
    fi

    echo "$content" | jq -c '[.[] | select(type == "object" and .type == "tool_use")]'
}

# Get usage from assistant message parts (takes last for SSE cumulative counts)
get_usage_from_parts() {
    local parts="$1"
    echo "$parts" | jq -c '
        [.[] | .message.usage // null | select(. != null)] | last // null
    '
}

# Find tool result and timestamp
# Returns JSON: {result: "...", timestamp: "..."}
find_tool_result_with_timestamp() {
    local tool_id="$1"
    local tool_results="$2"

    local result_data
    result_data=$(echo "$tool_results" | jq -c --arg id "$tool_id" '
        first(
            .[] |
            . as $msg |
            (if type == "object" and has("message") then .message.content elif type == "object" then .content else null end) as $content |
            if $content | type == "array" then
                $content[] |
                select(type == "object" and .type == "tool_result" and .tool_use_id == $id) |
                {
                    result: (
                        if .content | type == "array" then
                            [.content[] | select(type == "object" and .type == "text") | .text] | join(" ")
                        elif .content | type == "string" then
                            .content
                        else
                            .content | tostring
                        end
                    ),
                    timestamp: $msg.timestamp
                }
            else
                empty
            end
        ) // {result: "No result", timestamp: null}
    ')

    echo "$result_data"
}

# Merge assistant message parts
merge_assistant_parts() {
    local current_assistant_parts="$1"

    # Extract usage from parts (last one for SSE cumulative)
    local usage
    usage=$(get_usage_from_parts "$current_assistant_parts")

    echo "$current_assistant_parts" | jq -s \
        --argjson usage "$usage" \
        '
        .[0][0] as $base |
        (.[0] | map(if type == "object" and has("message") then .message.content elif type == "object" then .content else null end) | map(select(. != null))) as $contents |
        ($contents | map(
            if type == "string" then [{"type":"text","text":.}]
            elif type == "array" then .
            else [.]
            end
        ) | add // []) as $merged_content |
        ($merged_content | reduce .[] as $item (
            {result: [], buffer: null};
            if $item.type == "text" then
                if .buffer then .buffer.text += $item.text
                else .buffer = $item
                end
            else
                (if .buffer then .result += [.buffer] else . end) |
                .buffer = null | .result += [$item]
            end
        ) | if .buffer then .result + [.buffer] else .result end) as $final_content |
        $base |
        if type == "object" and has("message") then
            .message.content = $final_content |
            (if $usage != null then .message._usage = $usage else . end)
        elif type == "object" then
            .content = $final_content |
            (if $usage != null then ._usage = $usage else . end)
        else
            .
        end
    '
}

# Serialize run data for multipart upload
# Writes parts to temp files and outputs curl -F arguments (one per line)
serialize_for_multipart() {
    local operation="$1"  # "post" or "patch"
    local run_json="$2"   # Full run JSON
    local temp_dir="$3"   # Temp directory for this batch

    local run_id
    run_id=$(echo "$run_json" | jq -r '.id')

    # Extract inputs/outputs from main data
    local inputs
    inputs=$(echo "$run_json" | jq -c '.inputs // empty')

    local outputs
    outputs=$(echo "$run_json" | jq -c '.outputs // empty')

    local main_data
    main_data=$(echo "$run_json" | jq -c 'del(.inputs, .outputs)')

    # Part 1: Main run data with Content-Length header
    local main_file="$temp_dir/${operation}_${run_id}_main.json"
    echo "$main_data" > "$main_file"
    local main_size=$(get_file_size "$main_file")
    echo "-F"
    echo "${operation}.${run_id}=<${main_file};type=application/json;headers=Content-Length:${main_size}"

    # Part 2: Inputs (if present) with Content-Length header
    if [ "$inputs" != "null" ] && [ -n "$inputs" ]; then
        local inputs_file="$temp_dir/${operation}_${run_id}_inputs.json"
        echo "$inputs" > "$inputs_file"
        local inputs_size=$(get_file_size "$inputs_file")
        echo "-F"
        echo "${operation}.${run_id}.inputs=<${inputs_file};type=application/json;headers=Content-Length:${inputs_size}"
    fi

    # Part 3: Outputs (if present) with Content-Length header
    if [ "$outputs" != "null" ] && [ -n "$outputs" ]; then
        local outputs_file="$temp_dir/${operation}_${run_id}_outputs.json"
        echo "$outputs" > "$outputs_file"
        local outputs_size=$(get_file_size "$outputs_file")
        echo "-F"
        echo "${operation}.${run_id}.outputs=<${outputs_file};type=application/json;headers=Content-Length:${outputs_size}"
    fi
}

# Send batch of runs via multipart endpoint
send_multipart_batch() {
    local operation="$1"  # "post" or "patch"
    local batch_json="$2" # JSON array of runs

    # Parse batch size
    local batch_size
    batch_size=$(echo "$batch_json" | jq 'length')

    if [ "$batch_size" -eq 0 ]; then
        debug "No $operation runs to send"
        return 0
    fi

    # Create temp directory for this batch
    local temp_dir
    temp_dir=$(mktemp -d)

    # Build multipart curl command
    local curl_args=()
    curl_args+=("-s" "--max-time" "60" "-w" "\n%{http_code}" "-X" "POST")
    curl_args+=("-H" "x-api-key: $API_KEY")

    # Serialize each run and collect curl -F arguments
    while IFS= read -r run; do
        # Read arguments line by line (proper array handling, no word splitting)
        while IFS= read -r arg; do
            curl_args+=("$arg")
        done < <(serialize_for_multipart "$operation" "$run" "$temp_dir")
    done < <(echo "$batch_json" | jq -c '.[]')

    curl_args+=("$API_BASE/runs/multipart")

    # Execute curl
    local response
    local http_code

    response=$(curl "${curl_args[@]}" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | sed '$d')

    # Cleanup temp directory
    rm -rf "$temp_dir"

    if [ "$http_code" -lt 200 ] || [ "$http_code" -ge 300 ]; then
        log "ERROR" "Batch $operation failed: HTTP $http_code"
        log "ERROR" "Response: $response"
        return 1
    fi

    log "INFO" "Batch $operation succeeded: $batch_size runs"
    return 0
}

# Create LangSmith trace
create_trace() {
    local session_id="$1"
    local turn_num="$2"
    local user_msg="$3"
    local assistant_messages="$4"  # JSON array of assistant messages
    local tool_results="$5"

    # Initialize batch collectors for this trace
    local posts_batch="[]"
    local patches_batch="[]"

    local turn_id
    turn_id=$(uuidgen | tr '[:upper:]' '[:lower:]')

    local user_content
    user_content=$(format_content "$user_msg")

    local now
    now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Create dotted_order timestamp with microseconds (format: YYYYMMDDTHHMMSSffffffZ)
    local dotted_timestamp
    dotted_timestamp=$(date -u +"%Y%m%dT%H%M%S")
    local microseconds
    microseconds=$(get_microseconds)
    dotted_timestamp="${dotted_timestamp}${microseconds}Z"

    # Create turn run with dotted_order and trace_id
    # If parent exists, nest under it; otherwise turn is the root
    local turn_dotted_order
    local turn_trace_id
    if [ -n "$PARENT_RUN_ID" ]; then
        turn_dotted_order="${PARENT_DOTTED_ORDER}.${dotted_timestamp}${turn_id}"
        turn_trace_id="$EXPERIMENT_TRACE_ID"
    else
        turn_dotted_order="${dotted_timestamp}${turn_id}"
        turn_trace_id="$turn_id"
    fi

    local turn_data
    turn_data=$(jq -n \
        --arg id "$turn_id" \
        --arg trace_id "$turn_trace_id" \
        --arg name "Claude Code" \
        --arg project "$PROJECT" \
        --arg session "$session_id" \
        --arg time "$now" \
        --argjson content "$user_content" \
        --arg turn "$turn_num" \
        --arg dotted_order "$turn_dotted_order" \
        --arg parent_run_id "${PARENT_RUN_ID:-}" \
        '{
            id: $id,
            trace_id: $trace_id,
            name: $name,
            run_type: "chain",
            inputs: {messages: [{role: "user", content: $content}]},
            start_time: $time,
            dotted_order: $dotted_order,
            session_name: $project,
            extra: {metadata: {thread_id: $session}},
            tags: ["claude-code", ("turn-" + $turn)]
        }
        | if $parent_run_id != "" then .parent_run_id = $parent_run_id else . end
        ')

    local new_posts
    new_posts=$(echo "$posts_batch" | jq --argjson data "$turn_data" '. += [$data]')
    if [ -n "$new_posts" ]; then
        posts_batch="$new_posts"
    fi

    # Track this turn for cleanup on early exit
    CURRENT_TURN_ID="$turn_id"

    # Build final outputs array (accumulates all LLM responses)
    local all_outputs
    all_outputs=$(jq -n --argjson content "$user_content" '[{role: "user", content: $content}]')

    # Process each assistant message (each represents one LLM call)
    local llm_num=0
    local last_llm_end="$now"
    while IFS= read -r assistant_msg; do
        llm_num=$((llm_num + 1))

        # Extract timestamp from message for proper ordering
        local msg_timestamp
        msg_timestamp=$(echo "$assistant_msg" | jq -r '.timestamp // ""')

        # Use message timestamp for LLM start time
        local llm_start
        if [ -n "$msg_timestamp" ]; then
            llm_start="$msg_timestamp"
        elif [ $llm_num -eq 1 ]; then
            llm_start="$now"
        else
            llm_start="$last_llm_end"
        fi

        # Create assistant run
        local assistant_id
        assistant_id=$(uuidgen | tr '[:upper:]' '[:lower:]')

        local tool_uses
        tool_uses=$(get_tool_uses "$assistant_msg")

        local assistant_content
        assistant_content=$(format_content "$assistant_msg")

        # Extract model name from assistant message and strip date suffix
        # e.g., "claude-sonnet-4-5-20250929" -> "claude-sonnet-4-5"
        local model_name
        model_name=$(echo "$assistant_msg" | jq -r 'if type == "object" and has("message") then .message.model else empty end' | sed 's/-[0-9]\{8\}$//')

        # Extract usage data from assistant message (preserved by merge_assistant_parts)
        local msg_usage
        msg_usage=$(echo "$assistant_msg" | jq 'if type == "object" and has("message") then .message._usage // null elif type == "object" then ._usage // null else null end')

        # Build usage_metadata for LangSmith
        local usage_metadata
        if [ "$msg_usage" != "null" ] && [ -n "$msg_usage" ]; then
            usage_metadata=$(echo "$msg_usage" | jq '{
                input_tokens: ((.input_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0)),
                output_tokens: (.output_tokens // 0),
                input_token_details: {
                    cache_read: (.cache_read_input_tokens // 0),
                    cache_creation: (.cache_creation_input_tokens // 0)
                }
            }')
        else
            usage_metadata="null"
        fi

        # Build inputs for this LLM call (includes accumulated context)
        # Pipe through stdin to avoid ARG_MAX limits (all_outputs grows per-turn)
        local llm_inputs
        llm_inputs=$(echo "$all_outputs" | jq -c '{messages: .}')

        # Create dotted_order for assistant (child of turn)
        # Convert ISO timestamp to dotted_order format
        # From: 2025-12-16T17:44:04.397Z
        # To: 20251216T174404397000Z (milliseconds padded to microseconds)
        local assistant_timestamp
        if [ -n "$msg_timestamp" ]; then
            # Extract and convert timestamp from message
            assistant_timestamp=$(echo "$msg_timestamp" | sed 's/[-:]//g; s/\.\([0-9]*\)Z$/\1000Z/; s/T\([0-9]*\)\([0-9]\{3\}\)000Z$/T\1\2000Z/')
        else
            # Fallback to current time if no timestamp
            assistant_timestamp=$(date -u +"%Y%m%dT%H%M%S")
            local assistant_microseconds
            assistant_microseconds=$(get_microseconds)
            assistant_timestamp="${assistant_timestamp}${assistant_microseconds}Z"
        fi
        local assistant_dotted_order="${turn_dotted_order}.${assistant_timestamp}${assistant_id}"

        # Use the turn's trace_id for all children
        local trace_id="$turn_trace_id"

        # Build outputs for this LLM call
        local llm_outputs
        llm_outputs=$(jq -n --argjson content "$assistant_content" '[{role: "assistant", content: $content}]')

        # Track when this LLM iteration ends (after tools complete)
        local assistant_end

        # Create tool runs as siblings of the assistant run
        if [ "$(echo "$tool_uses" | jq 'length')" -gt 0 ]; then
            # First tool starts after LLM completes
            # Use llm_start as LLM end time approximation (we don't have separate end timestamp)
            local tool_start
            tool_start="$llm_start"

            # If there are multiple assistant parts, the last timestamp is closer to LLM end
            local llm_end_approx
            llm_end_approx=$(echo "$assistant_msg" | jq -r '.timestamp // ""')
            if [ -n "$llm_end_approx" ]; then
                tool_start="$llm_end_approx"
            fi

            while IFS= read -r tool; do
                local tool_id
                tool_id=$(uuidgen | tr '[:upper:]' '[:lower:]')

                local tool_name
                tool_name=$(echo "$tool" | jq -r '.name // "tool"')

                local tool_input
                tool_input=$(echo "$tool" | jq '.input // {}')

                local tool_use_id
                tool_use_id=$(echo "$tool" | jq -r '.id // ""')

                # Find tool result and extract timestamp from transcript
                local result_data
                result_data=$(find_tool_result_with_timestamp "$tool_use_id" "$tool_results")

                local result
                result=$(echo "$result_data" | jq -r '.result')

                local tool_result_timestamp
                tool_result_timestamp=$(echo "$result_data" | jq -r '.timestamp // ""')

                # Create dotted_order for tool (child of turn)
                # Use the tool result timestamp from transcript for proper ordering
                local tool_timestamp
                if [ -n "$tool_result_timestamp" ]; then
                    # Convert ISO timestamp to dotted_order format
                    # From: 2025-12-16T17:44:04.397Z
                    # To: 20251216T174404397000Z (milliseconds padded to microseconds)
                    tool_timestamp=$(echo "$tool_result_timestamp" | sed 's/[-:]//g; s/\.\([0-9]*\)Z$/\1000Z/; s/T\([0-9]*\)\([0-9]\{3\}\)000Z$/T\1\2000Z/')
                else
                    # Fallback to current time if no timestamp in transcript
                    tool_timestamp=$(date -u +"%Y%m%dT%H%M%S")
                    local tool_microseconds
                    tool_microseconds=$(get_microseconds)
                    tool_timestamp="${tool_timestamp}${tool_microseconds}Z"
                fi

                local tool_dotted_order="${turn_dotted_order}.${tool_timestamp}${tool_id}"

                # Use tool result timestamp for end time as well
                local tool_end
                if [ -n "$tool_result_timestamp" ]; then
                    tool_end="$tool_result_timestamp"
                else
                    tool_end=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
                fi

                # Tools are siblings of the assistant run (both children of turn run)
                # Include outputs + end_time directly in POST (avoids race with separate PATCH)
                local tool_data
                tool_data=$(echo "$result" | jq -Rs \
                    --arg id "$tool_id" \
                    --arg trace_id "$trace_id" \
                    --arg parent "$turn_id" \
                    --arg name "$tool_name" \
                    --arg project "$PROJECT" \
                    --arg start_time "$tool_start" \
                    --arg end_time "$tool_end" \
                    --argjson input "$tool_input" \
                    --arg dotted_order "$tool_dotted_order" \
                    '{
                        id: $id,
                        trace_id: $trace_id,
                        parent_run_id: $parent,
                        name: $name,
                        run_type: "tool",
                        inputs: {input: $input},
                        outputs: {output: .},
                        start_time: $start_time,
                        end_time: $end_time,
                        dotted_order: $dotted_order,
                        session_name: $project,
                        tags: ["tool"]
                    }')

                if [ -n "$tool_data" ]; then
                    local new_posts
                    new_posts=$(echo "$posts_batch" | jq --argjson data "$tool_data" '. += [$data]')
                    if [ -n "$new_posts" ]; then
                        posts_batch="$new_posts"
                    fi
                fi

                # Next tool starts after this one ends
                tool_start="$tool_end"

            done < <(echo "$tool_uses" | jq -c '.[]')

            # Assistant completes after all tools finish
            assistant_end="$tool_start"
        else
            # No tools, assistant completes immediately
            assistant_end=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        fi

        # Create LLM run with outputs included (avoids race with separate PATCH)
        # Build LLM run JSON. Pipe inputs through stdin to avoid ARG_MAX limits
        # (llm_inputs grows per-turn as conversation accumulates, can exceed 128KB)
        local assistant_data
        assistant_data=$(echo "$llm_inputs" | jq -c \
            --arg id "$assistant_id" \
            --arg trace_id "$trace_id" \
            --arg parent "$turn_id" \
            --arg name "Claude" \
            --arg project "$PROJECT" \
            --arg start_time "$llm_start" \
            --arg end_time "$assistant_end" \
            --argjson outputs "$llm_outputs" \
            --argjson usage_metadata "$usage_metadata" \
            --arg dotted_order "$assistant_dotted_order" \
            --arg model "$model_name" \
            '{
                id: $id,
                trace_id: $trace_id,
                parent_run_id: $parent,
                name: $name,
                run_type: "llm",
                inputs: .,
                outputs: ({messages: $outputs} + (if $usage_metadata != null then {usage_metadata: $usage_metadata} else {} end)),
                start_time: $start_time,
                end_time: $end_time,
                dotted_order: $dotted_order,
                session_name: $project,
                extra: {metadata: {ls_provider: "anthropic", ls_model_name: $model}},
                tags: [$model]
            }')

        if [ -n "$assistant_data" ]; then
            local new_posts
            new_posts=$(echo "$posts_batch" | jq --argjson data "$assistant_data" '. += [$data]')
            if [ -n "$new_posts" ]; then
                posts_batch="$new_posts"
            else
                log "WARN" "jq accumulation returned empty for LLM run $assistant_id, keeping previous batch"
            fi
        else
            log "WARN" "Empty assistant_data for LLM call $llm_num, skipping"
        fi

        # Save end time for next LLM start
        last_llm_end="$assistant_end"

        # Add to overall outputs
        all_outputs=$(echo "$all_outputs" | jq --argjson new "$llm_outputs" '. += $new')

        # Add tool results to accumulated context (for next LLM's inputs)
        if [ "$(echo "$tool_uses" | jq 'length')" -gt 0 ]; then
            while IFS= read -r tool; do
                local tool_use_id
                tool_use_id=$(echo "$tool" | jq -r '.id // ""')
                local result_data
                result_data=$(find_tool_result_with_timestamp "$tool_use_id" "$tool_results")
                local result
                result=$(echo "$result_data" | jq -r '.result')
                all_outputs=$(echo "$all_outputs" | jq \
                    --arg id "$tool_use_id" \
                    --arg result "$result" \
                    '. += [{role: "tool", tool_call_id: $id, content: [{type: "text", text: $result}]}]')
            done < <(echo "$tool_uses" | jq -c '.[]')
        fi

    done < <(echo "$assistant_messages" | jq -c '.[]')

    # Update turn run with all outputs
    # Filter out user messages from final outputs
    local turn_outputs
    turn_outputs=$(echo "$all_outputs" | jq '[.[] | select(.role != "user")]')

    # Use the last LLM's end time as the turn end time
    local turn_end="$last_llm_end"

    local turn_update
    turn_update=$(echo "$turn_outputs" | jq -c \
        --arg time "$turn_end" \
        --arg id "$turn_id" \
        --arg trace_id "$turn_trace_id" \
        --arg dotted_order "$turn_dotted_order" \
        --arg parent_run_id "${PARENT_RUN_ID:-}" \
        '{
            id: $id,
            trace_id: $trace_id,
            dotted_order: $dotted_order,
            outputs: {messages: .},
            end_time: $time
        }
        | if $parent_run_id != "" then .parent_run_id = $parent_run_id else . end')

    patches_batch=$(echo "$patches_batch" | jq --argjson data "$turn_update" '. += [$data]')

    # Send both batches
    send_multipart_batch "post" "$posts_batch" || true
    send_multipart_batch "patch" "$patches_batch" || true

    # Clear the tracked turn since it's now complete
    CURRENT_TURN_ID=""

    log "INFO" "Created turn $turn_num: $turn_id with $llm_num LLM call(s)"
}

# Main function
main() {
    # Track execution time
    local script_start
    script_start=$(date +%s)

    # Read hook input
    local hook_input
    hook_input=$(cat)

    # Check stop_hook_active flag
    if echo "$hook_input" | jq -e '.stop_hook_active == true' > /dev/null 2>&1; then
        debug "stop_hook_active=true, skipping"
        exit 0
    fi

    # Extract session info
    local session_id
    session_id=$(echo "$hook_input" | jq -r '.session_id // ""')

    local transcript_path
    transcript_path=$(echo "$hook_input" | jq -r '.transcript_path // ""' | sed "s|^~|$HOME|")

    if [ -z "$session_id" ] || [ ! -f "$transcript_path" ]; then
        log "WARN" "Invalid input: session=$session_id, transcript=$transcript_path"
        exit 0
    fi

    log "INFO" "Processing session $session_id"

    # Load state
    local state
    state=$(load_state)

    local last_line
    last_line=$(echo "$state" | jq -r --arg sid "$session_id" '.[$sid].last_line // -1')

    local turn_count
    turn_count=$(echo "$state" | jq -r --arg sid "$session_id" '.[$sid].turn_count // 0')

    # Parse new messages
    local new_messages
    new_messages=$(awk -v start="$last_line" 'NR > start + 1 && NF' "$transcript_path")

    if [ -z "$new_messages" ]; then
        debug "No new messages"
        exit 0
    fi

    local msg_count
    msg_count=$(echo "$new_messages" | wc -l)
    log "INFO" "Found $msg_count new messages"

    # Create parent "Claude Code Session" run to group all turns.
    # When experiment context is available, nest under the experiment run
    # so CC traces appear in the experiment row's trace tree.
    if [ -z "$PARENT_RUN_ID" ] && [ -n "$EXPERIMENT_RUN_ID" ]; then
        PARENT_RUN_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
        local parent_now
        parent_now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local parent_dotted_timestamp
        parent_dotted_timestamp=$(date -u +"%Y%m%dT%H%M%S")
        local parent_microseconds
        parent_microseconds=$(get_microseconds)
        parent_dotted_timestamp="${parent_dotted_timestamp}${parent_microseconds}Z"

        PARENT_DOTTED_ORDER="${EXPERIMENT_DOTTED_ORDER}.${parent_dotted_timestamp}${PARENT_RUN_ID}"

        local parent_data
        parent_data=$(jq -n \
            --arg id "$PARENT_RUN_ID" \
            --arg trace_id "$EXPERIMENT_TRACE_ID" \
            --arg parent_run_id "$EXPERIMENT_RUN_ID" \
            --arg name "Claude Code Session" \
            --arg project "$PROJECT" \
            --arg session "$session_id" \
            --arg time "$parent_now" \
            --arg dotted_order "$PARENT_DOTTED_ORDER" \
            '{
                id: $id,
                trace_id: $trace_id,
                parent_run_id: $parent_run_id,
                name: $name,
                run_type: "chain",
                inputs: {},
                start_time: $time,
                dotted_order: $dotted_order,
                session_name: $project,
                extra: {metadata: {thread_id: $session}},
                tags: ["claude-code", "session"]
            }')

        send_multipart_batch "post" "[$parent_data]" || true
        log "INFO" "Created parent run $PARENT_RUN_ID under experiment $EXPERIMENT_RUN_ID"
    fi

    # Group into turns
    local current_user=""
    local current_assistants="[]"  # Array of assistant messages
    local current_msg_id=""  # Current assistant message ID
    local current_assistant_parts="[]"  # Parts of current assistant message
    local current_tool_results="[]"
    local turns=0
    local new_last_line=$last_line

    while IFS= read -r line; do
        new_last_line=$((new_last_line + 1))

        if [ -z "$line" ]; then
            continue
        fi

        local role
        role=$(echo "$line" | jq -r 'if type == "object" and has("message") then .message.role elif type == "object" then .role else "unknown" end')

        if [ "$role" = "user" ]; then
            if [ "$(is_tool_result "$line")" = "true" ]; then
                # Add to tool results
                current_tool_results=$(echo "$current_tool_results" | jq --argjson msg "$line" '. += [$msg]')
            else
                # New turn - finalize any pending assistant message
                if [ -n "$current_msg_id" ] && [ "$(echo "$current_assistant_parts" | jq 'length')" -gt 0 ]; then
                    # Merge parts and add to assistants array
                    local merged
                    merged=$(merge_assistant_parts "$current_assistant_parts")
                    current_assistants=$(echo "$current_assistants" | jq --argjson msg "$merged" '. += [$msg]')
                    current_assistant_parts="[]"
                    current_msg_id=""
                fi

                # Create trace for previous turn
                if [ -n "$current_user" ] && [ "$(echo "$current_assistants" | jq 'length')" -gt 0 ]; then
                    turns=$((turns + 1))
                    local turn_num=$((turn_count + turns))
                    create_trace "$session_id" "$turn_num" "$current_user" "$current_assistants" "$current_tool_results" || true
                fi

                # Start new turn
                current_user="$line"
                current_assistants="[]"
                current_assistant_parts="[]"
                current_msg_id=""
                current_tool_results="[]"
            fi
        elif [ "$role" = "assistant" ]; then
            # Get message ID
            local msg_id
            msg_id=$(echo "$line" | jq -r 'if type == "object" and has("message") then .message.id else "" end')

            if [ -z "$msg_id" ]; then
                # No message ID, treat as continuation of current message
                current_assistant_parts=$(echo "$current_assistant_parts" | jq --argjson msg "$line" '. += [$msg]')
            elif [ "$msg_id" = "$current_msg_id" ]; then
                # Same message ID, add to current parts
                current_assistant_parts=$(echo "$current_assistant_parts" | jq --argjson msg "$line" '. += [$msg]')
            else
                # New message ID - finalize previous message if any
                if [ -n "$current_msg_id" ] && [ "$(echo "$current_assistant_parts" | jq 'length')" -gt 0 ]; then
                    # Merge parts and add to assistants array
                    local merged
                    merged=$(merge_assistant_parts "$current_assistant_parts")
                    current_assistants=$(echo "$current_assistants" | jq --argjson msg "$merged" '. += [$msg]')
                fi

                # Start new assistant message
                current_msg_id="$msg_id"
                current_assistant_parts=$(jq -n --argjson msg "$line" '[$msg]')
            fi
        fi
    done <<< "$new_messages"

    # Process final turn - finalize any pending assistant message
    if [ -n "$current_msg_id" ] && [ "$(echo "$current_assistant_parts" | jq 'length')" -gt 0 ]; then
        local merged
        merged=$(merge_assistant_parts "$current_assistant_parts")
        current_assistants=$(echo "$current_assistants" | jq --argjson msg "$merged" '. += [$msg]')
    fi

    if [ -n "$current_user" ] && [ "$(echo "$current_assistants" | jq 'length')" -gt 0 ]; then
        turns=$((turns + 1))
        local turn_num=$((turn_count + turns))
        create_trace "$session_id" "$turn_num" "$current_user" "$current_assistants" "$current_tool_results" || true
    fi

    # Close parent run if one was created
    if [ -n "$PARENT_RUN_ID" ]; then
        local parent_end
        parent_end=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local parent_update
        parent_update=$(jq -n \
            --arg id "$PARENT_RUN_ID" \
            --arg trace_id "$EXPERIMENT_TRACE_ID" \
            --arg parent_run_id "$EXPERIMENT_RUN_ID" \
            --arg dotted_order "$PARENT_DOTTED_ORDER" \
            --arg time "$parent_end" \
            '{
                id: $id,
                trace_id: $trace_id,
                parent_run_id: $parent_run_id,
                dotted_order: $dotted_order,
                outputs: {},
                end_time: $time
            }')
        send_multipart_batch "patch" "[$parent_update]" || true
        log "INFO" "Closed parent run $PARENT_RUN_ID"
    fi

    # Update state
    local updated
    updated=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    state=$(echo "$state" | jq \
        --arg sid "$session_id" \
        --arg line "$new_last_line" \
        --arg count "$((turn_count + turns))" \
        --arg time "$updated" \
        '.[$sid] = {last_line: ($line | tonumber), turn_count: ($count | tonumber), updated: $time}')

    save_state "$state"

    # Log execution time
    local script_end
    script_end=$(date +%s)
    local duration=$((script_end - script_start))

    log "INFO" "Processed $turns turns in ${duration}s"
    if [ "$duration" -gt 180 ]; then
        log "WARN" "Hook took ${duration}s (>3min), consider optimizing"
    fi
}

# Run main
main

exit 0