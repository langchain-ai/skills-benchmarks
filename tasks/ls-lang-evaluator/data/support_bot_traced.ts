/**
 * Customer support chatbot with multi-step processing.
 * WITH LangSmith tracing - this is the ground truth for validation.
 */

import OpenAI from "openai";
import { traceable } from "langsmith/traceable";
import { wrapOpenAI } from "langsmith/wrappers";
import "dotenv/config";

// Wrap the OpenAI client so LLM calls are automatically traced in LangSmith.
const client = wrapOpenAI(new OpenAI());

interface Entities {
  order_id: string | null;
  product_name: string | null;
  customer_emotion: string;
}

interface OrderInfo {
  status: string;
  eta: string | null;
  item: string;
}

const classifyIntent = traceable(
  async (message: string): Promise<string> => {
    /**
     * Classify the customer's intent.
     */
    const response = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            "Classify the customer message into one of: ORDER_STATUS, REFUND_REQUEST, PRODUCT_QUESTION, COMPLAINT, OTHER. Respond with just the category.",
        },
        { role: "user", content: message },
      ],
    });
    return response.choices[0].message.content?.trim() ?? "OTHER";
  },
  { name: "classify_intent" }
);

const extractEntities = traceable(
  async (message: string): Promise<Entities> => {
    /**
     * Extract relevant entities from the message.
     */
    const response = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            'Extract entities from the message. Return JSON with keys: order_id (string or null), product_name (string or null), customer_emotion (string). Example: {"order_id": "12345", "product_name": null, "customer_emotion": "frustrated"}',
        },
        { role: "user", content: message },
      ],
    });
    try {
      return JSON.parse(response.choices[0].message.content ?? "{}");
    } catch {
      return { order_id: null, product_name: null, customer_emotion: "neutral" };
    }
  },
  { name: "extract_entities" }
);

const lookupOrder = traceable(
  (orderId: string): OrderInfo | null => {
    /**
     * Mock order lookup.
     */
    const orders: Record<string, OrderInfo> = {
      "12345": { status: "shipped", eta: "Feb 5", item: "Wireless Headphones" },
      "67890": { status: "processing", eta: "Feb 8", item: "USB-C Cable" },
      "11111": { status: "delivered", eta: null, item: "Phone Case" },
    };
    return orders[orderId] ?? null;
  },
  { name: "lookup_order" }
);

const generateResponse = traceable(
  async (
    intent: string,
    entities: Entities,
    orderInfo: OrderInfo | null
  ): Promise<string> => {
    /**
     * Generate a helpful response based on analysis.
     */
    const contextParts = [
      `Intent: ${intent}`,
      `Customer emotion: ${entities.customer_emotion ?? "neutral"}`,
    ];

    if (orderInfo) {
      contextParts.push(`Order status: ${orderInfo.status}`);
      contextParts.push(`Item: ${orderInfo.item}`);
      if (orderInfo.eta) {
        contextParts.push(`ETA: ${orderInfo.eta}`);
      }
    }

    const context = contextParts.join("\n");

    const response = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: `You are a helpful customer support agent. Based on the following context, write a brief, empathetic response.\n\n${context}`,
        },
        { role: "user", content: "Please help me with my issue." },
      ],
    });
    return response.choices[0].message.content ?? "";
  },
  { name: "generate_response" }
);

const handleSupportRequest = traceable(
  async (message: string): Promise<string> => {
    /**
     * Main pipeline: classify -> extract -> lookup -> respond.
     */
    const intent = await classifyIntent(message);
    const entities = await extractEntities(message);

    let orderInfo: OrderInfo | null = null;
    if (entities.order_id) {
      orderInfo = await lookupOrder(entities.order_id);
    }

    const response = await generateResponse(intent, entities, orderInfo);
    return response;
  },
  { name: "handle_support_request", run_type: "chain" }
);

// Main execution
async function main() {
  const testMessages = [
    "Where is my order #12345? I've been waiting forever!",
    "I want a refund for the broken headphones I received.",
    "Does the blue widget come in size large?",
  ];

  for (const msg of testMessages) {
    console.log("\n" + "=".repeat(50));
    console.log(`Customer: ${msg}`);
    console.log("=".repeat(50));
    const response = await handleSupportRequest(msg);
    console.log(`Agent: ${response}`);
  }
}

main().catch(console.error);
