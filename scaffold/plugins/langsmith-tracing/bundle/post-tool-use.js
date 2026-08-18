#!/usr/bin/env node
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __commonJS = (cb, mod) => function __require() {
  return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// node_modules/.pnpm/eventemitter3@4.0.7/node_modules/eventemitter3/index.js
var require_eventemitter3 = __commonJS({
  "node_modules/.pnpm/eventemitter3@4.0.7/node_modules/eventemitter3/index.js"(exports, module) {
    "use strict";
    var has = Object.prototype.hasOwnProperty;
    var prefix = "~";
    function Events() {
    }
    if (Object.create) {
      Events.prototype = /* @__PURE__ */ Object.create(null);
      if (!new Events().__proto__) prefix = false;
    }
    function EE(fn, context, once) {
      this.fn = fn;
      this.context = context;
      this.once = once || false;
    }
    function addListener(emitter, event, fn, context, once) {
      if (typeof fn !== "function") {
        throw new TypeError("The listener must be a function");
      }
      var listener = new EE(fn, context || emitter, once), evt = prefix ? prefix + event : event;
      if (!emitter._events[evt]) emitter._events[evt] = listener, emitter._eventsCount++;
      else if (!emitter._events[evt].fn) emitter._events[evt].push(listener);
      else emitter._events[evt] = [emitter._events[evt], listener];
      return emitter;
    }
    function clearEvent(emitter, evt) {
      if (--emitter._eventsCount === 0) emitter._events = new Events();
      else delete emitter._events[evt];
    }
    function EventEmitter() {
      this._events = new Events();
      this._eventsCount = 0;
    }
    EventEmitter.prototype.eventNames = function eventNames() {
      var names = [], events, name;
      if (this._eventsCount === 0) return names;
      for (name in events = this._events) {
        if (has.call(events, name)) names.push(prefix ? name.slice(1) : name);
      }
      if (Object.getOwnPropertySymbols) {
        return names.concat(Object.getOwnPropertySymbols(events));
      }
      return names;
    };
    EventEmitter.prototype.listeners = function listeners(event) {
      var evt = prefix ? prefix + event : event, handlers = this._events[evt];
      if (!handlers) return [];
      if (handlers.fn) return [handlers.fn];
      for (var i = 0, l = handlers.length, ee = new Array(l); i < l; i++) {
        ee[i] = handlers[i].fn;
      }
      return ee;
    };
    EventEmitter.prototype.listenerCount = function listenerCount(event) {
      var evt = prefix ? prefix + event : event, listeners = this._events[evt];
      if (!listeners) return 0;
      if (listeners.fn) return 1;
      return listeners.length;
    };
    EventEmitter.prototype.emit = function emit(event, a1, a2, a3, a4, a5) {
      var evt = prefix ? prefix + event : event;
      if (!this._events[evt]) return false;
      var listeners = this._events[evt], len = arguments.length, args, i;
      if (listeners.fn) {
        if (listeners.once) this.removeListener(event, listeners.fn, void 0, true);
        switch (len) {
          case 1:
            return listeners.fn.call(listeners.context), true;
          case 2:
            return listeners.fn.call(listeners.context, a1), true;
          case 3:
            return listeners.fn.call(listeners.context, a1, a2), true;
          case 4:
            return listeners.fn.call(listeners.context, a1, a2, a3), true;
          case 5:
            return listeners.fn.call(listeners.context, a1, a2, a3, a4), true;
          case 6:
            return listeners.fn.call(listeners.context, a1, a2, a3, a4, a5), true;
        }
        for (i = 1, args = new Array(len - 1); i < len; i++) {
          args[i - 1] = arguments[i];
        }
        listeners.fn.apply(listeners.context, args);
      } else {
        var length = listeners.length, j;
        for (i = 0; i < length; i++) {
          if (listeners[i].once) this.removeListener(event, listeners[i].fn, void 0, true);
          switch (len) {
            case 1:
              listeners[i].fn.call(listeners[i].context);
              break;
            case 2:
              listeners[i].fn.call(listeners[i].context, a1);
              break;
            case 3:
              listeners[i].fn.call(listeners[i].context, a1, a2);
              break;
            case 4:
              listeners[i].fn.call(listeners[i].context, a1, a2, a3);
              break;
            default:
              if (!args) for (j = 1, args = new Array(len - 1); j < len; j++) {
                args[j - 1] = arguments[j];
              }
              listeners[i].fn.apply(listeners[i].context, args);
          }
        }
      }
      return true;
    };
    EventEmitter.prototype.on = function on(event, fn, context) {
      return addListener(this, event, fn, context, false);
    };
    EventEmitter.prototype.once = function once(event, fn, context) {
      return addListener(this, event, fn, context, true);
    };
    EventEmitter.prototype.removeListener = function removeListener(event, fn, context, once) {
      var evt = prefix ? prefix + event : event;
      if (!this._events[evt]) return this;
      if (!fn) {
        clearEvent(this, evt);
        return this;
      }
      var listeners = this._events[evt];
      if (listeners.fn) {
        if (listeners.fn === fn && (!once || listeners.once) && (!context || listeners.context === context)) {
          clearEvent(this, evt);
        }
      } else {
        for (var i = 0, events = [], length = listeners.length; i < length; i++) {
          if (listeners[i].fn !== fn || once && !listeners[i].once || context && listeners[i].context !== context) {
            events.push(listeners[i]);
          }
        }
        if (events.length) this._events[evt] = events.length === 1 ? events[0] : events;
        else clearEvent(this, evt);
      }
      return this;
    };
    EventEmitter.prototype.removeAllListeners = function removeAllListeners(event) {
      var evt;
      if (event) {
        evt = prefix ? prefix + event : event;
        if (this._events[evt]) clearEvent(this, evt);
      } else {
        this._events = new Events();
        this._eventsCount = 0;
      }
      return this;
    };
    EventEmitter.prototype.off = EventEmitter.prototype.removeListener;
    EventEmitter.prototype.addListener = EventEmitter.prototype.on;
    EventEmitter.prefixed = prefix;
    EventEmitter.EventEmitter = EventEmitter;
    if ("undefined" !== typeof module) {
      module.exports = EventEmitter;
    }
  }
});

// node_modules/.pnpm/p-finally@1.0.0/node_modules/p-finally/index.js
var require_p_finally = __commonJS({
  "node_modules/.pnpm/p-finally@1.0.0/node_modules/p-finally/index.js"(exports, module) {
    "use strict";
    module.exports = (promise, onFinally) => {
      onFinally = onFinally || (() => {
      });
      return promise.then(
        (val) => new Promise((resolve) => {
          resolve(onFinally());
        }).then(() => val),
        (err) => new Promise((resolve) => {
          resolve(onFinally());
        }).then(() => {
          throw err;
        })
      );
    };
  }
});

// node_modules/.pnpm/p-timeout@3.2.0/node_modules/p-timeout/index.js
var require_p_timeout = __commonJS({
  "node_modules/.pnpm/p-timeout@3.2.0/node_modules/p-timeout/index.js"(exports, module) {
    "use strict";
    var pFinally = require_p_finally();
    var TimeoutError = class extends Error {
      constructor(message) {
        super(message);
        this.name = "TimeoutError";
      }
    };
    var pTimeout = (promise, milliseconds, fallback) => new Promise((resolve, reject) => {
      if (typeof milliseconds !== "number" || milliseconds < 0) {
        throw new TypeError("Expected `milliseconds` to be a positive number");
      }
      if (milliseconds === Infinity) {
        resolve(promise);
        return;
      }
      const timer = setTimeout(() => {
        if (typeof fallback === "function") {
          try {
            resolve(fallback());
          } catch (error2) {
            reject(error2);
          }
          return;
        }
        const message = typeof fallback === "string" ? fallback : `Promise timed out after ${milliseconds} milliseconds`;
        const timeoutError = fallback instanceof Error ? fallback : new TimeoutError(message);
        if (typeof promise.cancel === "function") {
          promise.cancel();
        }
        reject(timeoutError);
      }, milliseconds);
      pFinally(
        // eslint-disable-next-line promise/prefer-await-to-then
        promise.then(resolve, reject),
        () => {
          clearTimeout(timer);
        }
      );
    });
    module.exports = pTimeout;
    module.exports.default = pTimeout;
    module.exports.TimeoutError = TimeoutError;
  }
});

// node_modules/.pnpm/p-queue@6.6.2/node_modules/p-queue/dist/lower-bound.js
var require_lower_bound = __commonJS({
  "node_modules/.pnpm/p-queue@6.6.2/node_modules/p-queue/dist/lower-bound.js"(exports) {
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    function lowerBound(array, value, comparator) {
      let first = 0;
      let count = array.length;
      while (count > 0) {
        const step = count / 2 | 0;
        let it = first + step;
        if (comparator(array[it], value) <= 0) {
          first = ++it;
          count -= step + 1;
        } else {
          count = step;
        }
      }
      return first;
    }
    exports.default = lowerBound;
  }
});

// node_modules/.pnpm/p-queue@6.6.2/node_modules/p-queue/dist/priority-queue.js
var require_priority_queue = __commonJS({
  "node_modules/.pnpm/p-queue@6.6.2/node_modules/p-queue/dist/priority-queue.js"(exports) {
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var lower_bound_1 = require_lower_bound();
    var PriorityQueue = class {
      constructor() {
        this._queue = [];
      }
      enqueue(run, options) {
        options = Object.assign({ priority: 0 }, options);
        const element = {
          priority: options.priority,
          run
        };
        if (this.size && this._queue[this.size - 1].priority >= options.priority) {
          this._queue.push(element);
          return;
        }
        const index = lower_bound_1.default(this._queue, element, (a, b) => b.priority - a.priority);
        this._queue.splice(index, 0, element);
      }
      dequeue() {
        const item = this._queue.shift();
        return item === null || item === void 0 ? void 0 : item.run;
      }
      filter(options) {
        return this._queue.filter((element) => element.priority === options.priority).map((element) => element.run);
      }
      get size() {
        return this._queue.length;
      }
    };
    exports.default = PriorityQueue;
  }
});

// node_modules/.pnpm/p-queue@6.6.2/node_modules/p-queue/dist/index.js
var require_dist = __commonJS({
  "node_modules/.pnpm/p-queue@6.6.2/node_modules/p-queue/dist/index.js"(exports) {
    "use strict";
    Object.defineProperty(exports, "__esModule", { value: true });
    var EventEmitter = require_eventemitter3();
    var p_timeout_1 = require_p_timeout();
    var priority_queue_1 = require_priority_queue();
    var empty = () => {
    };
    var timeoutError = new p_timeout_1.TimeoutError();
    var PQueue2 = class extends EventEmitter {
      constructor(options) {
        var _a, _b, _c, _d;
        super();
        this._intervalCount = 0;
        this._intervalEnd = 0;
        this._pendingCount = 0;
        this._resolveEmpty = empty;
        this._resolveIdle = empty;
        options = Object.assign({ carryoverConcurrencyCount: false, intervalCap: Infinity, interval: 0, concurrency: Infinity, autoStart: true, queueClass: priority_queue_1.default }, options);
        if (!(typeof options.intervalCap === "number" && options.intervalCap >= 1)) {
          throw new TypeError(`Expected \`intervalCap\` to be a number from 1 and up, got \`${(_b = (_a = options.intervalCap) === null || _a === void 0 ? void 0 : _a.toString()) !== null && _b !== void 0 ? _b : ""}\` (${typeof options.intervalCap})`);
        }
        if (options.interval === void 0 || !(Number.isFinite(options.interval) && options.interval >= 0)) {
          throw new TypeError(`Expected \`interval\` to be a finite number >= 0, got \`${(_d = (_c = options.interval) === null || _c === void 0 ? void 0 : _c.toString()) !== null && _d !== void 0 ? _d : ""}\` (${typeof options.interval})`);
        }
        this._carryoverConcurrencyCount = options.carryoverConcurrencyCount;
        this._isIntervalIgnored = options.intervalCap === Infinity || options.interval === 0;
        this._intervalCap = options.intervalCap;
        this._interval = options.interval;
        this._queue = new options.queueClass();
        this._queueClass = options.queueClass;
        this.concurrency = options.concurrency;
        this._timeout = options.timeout;
        this._throwOnTimeout = options.throwOnTimeout === true;
        this._isPaused = options.autoStart === false;
      }
      get _doesIntervalAllowAnother() {
        return this._isIntervalIgnored || this._intervalCount < this._intervalCap;
      }
      get _doesConcurrentAllowAnother() {
        return this._pendingCount < this._concurrency;
      }
      _next() {
        this._pendingCount--;
        this._tryToStartAnother();
        this.emit("next");
      }
      _resolvePromises() {
        this._resolveEmpty();
        this._resolveEmpty = empty;
        if (this._pendingCount === 0) {
          this._resolveIdle();
          this._resolveIdle = empty;
          this.emit("idle");
        }
      }
      _onResumeInterval() {
        this._onInterval();
        this._initializeIntervalIfNeeded();
        this._timeoutId = void 0;
      }
      _isIntervalPaused() {
        const now = Date.now();
        if (this._intervalId === void 0) {
          const delay = this._intervalEnd - now;
          if (delay < 0) {
            this._intervalCount = this._carryoverConcurrencyCount ? this._pendingCount : 0;
          } else {
            if (this._timeoutId === void 0) {
              this._timeoutId = setTimeout(() => {
                this._onResumeInterval();
              }, delay);
            }
            return true;
          }
        }
        return false;
      }
      _tryToStartAnother() {
        if (this._queue.size === 0) {
          if (this._intervalId) {
            clearInterval(this._intervalId);
          }
          this._intervalId = void 0;
          this._resolvePromises();
          return false;
        }
        if (!this._isPaused) {
          const canInitializeInterval = !this._isIntervalPaused();
          if (this._doesIntervalAllowAnother && this._doesConcurrentAllowAnother) {
            const job = this._queue.dequeue();
            if (!job) {
              return false;
            }
            this.emit("active");
            job();
            if (canInitializeInterval) {
              this._initializeIntervalIfNeeded();
            }
            return true;
          }
        }
        return false;
      }
      _initializeIntervalIfNeeded() {
        if (this._isIntervalIgnored || this._intervalId !== void 0) {
          return;
        }
        this._intervalId = setInterval(() => {
          this._onInterval();
        }, this._interval);
        this._intervalEnd = Date.now() + this._interval;
      }
      _onInterval() {
        if (this._intervalCount === 0 && this._pendingCount === 0 && this._intervalId) {
          clearInterval(this._intervalId);
          this._intervalId = void 0;
        }
        this._intervalCount = this._carryoverConcurrencyCount ? this._pendingCount : 0;
        this._processQueue();
      }
      /**
      Executes all queued functions until it reaches the limit.
      */
      _processQueue() {
        while (this._tryToStartAnother()) {
        }
      }
      get concurrency() {
        return this._concurrency;
      }
      set concurrency(newConcurrency) {
        if (!(typeof newConcurrency === "number" && newConcurrency >= 1)) {
          throw new TypeError(`Expected \`concurrency\` to be a number from 1 and up, got \`${newConcurrency}\` (${typeof newConcurrency})`);
        }
        this._concurrency = newConcurrency;
        this._processQueue();
      }
      /**
      Adds a sync or async task to the queue. Always returns a promise.
      */
      async add(fn, options = {}) {
        return new Promise((resolve, reject) => {
          const run = async () => {
            this._pendingCount++;
            this._intervalCount++;
            try {
              const operation = this._timeout === void 0 && options.timeout === void 0 ? fn() : p_timeout_1.default(Promise.resolve(fn()), options.timeout === void 0 ? this._timeout : options.timeout, () => {
                if (options.throwOnTimeout === void 0 ? this._throwOnTimeout : options.throwOnTimeout) {
                  reject(timeoutError);
                }
                return void 0;
              });
              resolve(await operation);
            } catch (error2) {
              reject(error2);
            }
            this._next();
          };
          this._queue.enqueue(run, options);
          this._tryToStartAnother();
          this.emit("add");
        });
      }
      /**
          Same as `.add()`, but accepts an array of sync or async functions.
      
          @returns A promise that resolves when all functions are resolved.
          */
      async addAll(functions, options) {
        return Promise.all(functions.map(async (function_) => this.add(function_, options)));
      }
      /**
      Start (or resume) executing enqueued tasks within concurrency limit. No need to call this if queue is not paused (via `options.autoStart = false` or by `.pause()` method.)
      */
      start() {
        if (!this._isPaused) {
          return this;
        }
        this._isPaused = false;
        this._processQueue();
        return this;
      }
      /**
      Put queue execution on hold.
      */
      pause() {
        this._isPaused = true;
      }
      /**
      Clear the queue.
      */
      clear() {
        this._queue = new this._queueClass();
      }
      /**
          Can be called multiple times. Useful if you for example add additional items at a later time.
      
          @returns A promise that settles when the queue becomes empty.
          */
      async onEmpty() {
        if (this._queue.size === 0) {
          return;
        }
        return new Promise((resolve) => {
          const existingResolve = this._resolveEmpty;
          this._resolveEmpty = () => {
            existingResolve();
            resolve();
          };
        });
      }
      /**
          The difference with `.onEmpty` is that `.onIdle` guarantees that all work from the queue has finished. `.onEmpty` merely signals that the queue is empty, but it could mean that some promises haven't completed yet.
      
          @returns A promise that settles when the queue becomes empty, and all promises have completed; `queue.size === 0 && queue.pending === 0`.
          */
      async onIdle() {
        if (this._pendingCount === 0 && this._queue.size === 0) {
          return;
        }
        return new Promise((resolve) => {
          const existingResolve = this._resolveIdle;
          this._resolveIdle = () => {
            existingResolve();
            resolve();
          };
        });
      }
      /**
      Size of the queue.
      */
      get size() {
        return this._queue.size;
      }
      /**
          Size of the queue, filtered by the given options.
      
          For example, this can be used to find the number of items remaining in the queue with a specific priority level.
          */
      sizeBy(options) {
        return this._queue.filter(options).length;
      }
      /**
      Number of pending promises.
      */
      get pending() {
        return this._pendingCount;
      }
      /**
      Whether the queue is currently paused.
      */
      get isPaused() {
        return this._isPaused;
      }
      get timeout() {
        return this._timeout;
      }
      /**
      Set the timeout for future operations.
      */
      set timeout(milliseconds) {
        this._timeout = milliseconds;
      }
    };
    exports.default = PQueue2;
  }
});

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/regex.js
var regex_default = /^(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$/i;

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/validate.js
function validate(uuid) {
  return typeof uuid === "string" && regex_default.test(uuid);
}
var validate_default = validate;

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/parse.js
function parse(uuid) {
  if (!validate_default(uuid)) {
    throw TypeError("Invalid UUID");
  }
  let v;
  const arr2 = new Uint8Array(16);
  arr2[0] = (v = parseInt(uuid.slice(0, 8), 16)) >>> 24;
  arr2[1] = v >>> 16 & 255;
  arr2[2] = v >>> 8 & 255;
  arr2[3] = v & 255;
  arr2[4] = (v = parseInt(uuid.slice(9, 13), 16)) >>> 8;
  arr2[5] = v & 255;
  arr2[6] = (v = parseInt(uuid.slice(14, 18), 16)) >>> 8;
  arr2[7] = v & 255;
  arr2[8] = (v = parseInt(uuid.slice(19, 23), 16)) >>> 8;
  arr2[9] = v & 255;
  arr2[10] = (v = parseInt(uuid.slice(24, 36), 16)) / 1099511627776 & 255;
  arr2[11] = v / 4294967296 & 255;
  arr2[12] = v >>> 24 & 255;
  arr2[13] = v >>> 16 & 255;
  arr2[14] = v >>> 8 & 255;
  arr2[15] = v & 255;
  return arr2;
}
var parse_default = parse;

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/stringify.js
var byteToHex = [];
for (let i = 0; i < 256; ++i) {
  byteToHex.push((i + 256).toString(16).slice(1));
}
function unsafeStringify(arr2, offset = 0) {
  return (byteToHex[arr2[offset + 0]] + byteToHex[arr2[offset + 1]] + byteToHex[arr2[offset + 2]] + byteToHex[arr2[offset + 3]] + "-" + byteToHex[arr2[offset + 4]] + byteToHex[arr2[offset + 5]] + "-" + byteToHex[arr2[offset + 6]] + byteToHex[arr2[offset + 7]] + "-" + byteToHex[arr2[offset + 8]] + byteToHex[arr2[offset + 9]] + "-" + byteToHex[arr2[offset + 10]] + byteToHex[arr2[offset + 11]] + byteToHex[arr2[offset + 12]] + byteToHex[arr2[offset + 13]] + byteToHex[arr2[offset + 14]] + byteToHex[arr2[offset + 15]]).toLowerCase();
}

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/rng.js
import crypto from "node:crypto";
var rnds8Pool = new Uint8Array(256);
var poolPtr = rnds8Pool.length;
function rng() {
  if (poolPtr > rnds8Pool.length - 16) {
    crypto.randomFillSync(rnds8Pool);
    poolPtr = 0;
  }
  return rnds8Pool.slice(poolPtr, poolPtr += 16);
}

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/v35.js
function stringToBytes(str) {
  str = unescape(encodeURIComponent(str));
  const bytes = [];
  for (let i = 0; i < str.length; ++i) {
    bytes.push(str.charCodeAt(i));
  }
  return bytes;
}
var DNS = "6ba7b810-9dad-11d1-80b4-00c04fd430c8";
var URL2 = "6ba7b811-9dad-11d1-80b4-00c04fd430c8";
function v35(name, version, hashfunc) {
  function generateUUID(value, namespace, buf, offset) {
    var _namespace;
    if (typeof value === "string") {
      value = stringToBytes(value);
    }
    if (typeof namespace === "string") {
      namespace = parse_default(namespace);
    }
    if (((_namespace = namespace) === null || _namespace === void 0 ? void 0 : _namespace.length) !== 16) {
      throw TypeError("Namespace must be array-like (16 iterable integer values, 0-255)");
    }
    let bytes = new Uint8Array(16 + value.length);
    bytes.set(namespace);
    bytes.set(value, namespace.length);
    bytes = hashfunc(bytes);
    bytes[6] = bytes[6] & 15 | version;
    bytes[8] = bytes[8] & 63 | 128;
    if (buf) {
      offset = offset || 0;
      for (let i = 0; i < 16; ++i) {
        buf[offset + i] = bytes[i];
      }
      return buf;
    }
    return unsafeStringify(bytes);
  }
  try {
    generateUUID.name = name;
  } catch (err) {
  }
  generateUUID.DNS = DNS;
  generateUUID.URL = URL2;
  return generateUUID;
}

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/native.js
import crypto2 from "node:crypto";
var native_default = {
  randomUUID: crypto2.randomUUID
};

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/v4.js
function v4(options, buf, offset) {
  if (native_default.randomUUID && !buf && !options) {
    return native_default.randomUUID();
  }
  options = options || {};
  const rnds = options.random || (options.rng || rng)();
  rnds[6] = rnds[6] & 15 | 64;
  rnds[8] = rnds[8] & 63 | 128;
  if (buf) {
    offset = offset || 0;
    for (let i = 0; i < 16; ++i) {
      buf[offset + i] = rnds[i];
    }
    return buf;
  }
  return unsafeStringify(rnds);
}
var v4_default = v4;

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/sha1.js
import crypto3 from "node:crypto";
function sha1(bytes) {
  if (Array.isArray(bytes)) {
    bytes = Buffer.from(bytes);
  } else if (typeof bytes === "string") {
    bytes = Buffer.from(bytes, "utf8");
  }
  return crypto3.createHash("sha1").update(bytes).digest();
}
var sha1_default = sha1;

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/v5.js
var v5 = v35("v5", 80, sha1_default);
var v5_default = v5;

// node_modules/.pnpm/uuid@10.0.0/node_modules/uuid/dist/esm-node/v7.js
var _seqLow = null;
var _seqHigh = null;
var _msecs = 0;
function v7(options, buf, offset) {
  options = options || {};
  let i = buf && offset || 0;
  const b = buf || new Uint8Array(16);
  const rnds = options.random || (options.rng || rng)();
  const msecs = options.msecs !== void 0 ? options.msecs : Date.now();
  let seq = options.seq !== void 0 ? options.seq : null;
  let seqHigh = _seqHigh;
  let seqLow = _seqLow;
  if (msecs > _msecs && options.msecs === void 0) {
    _msecs = msecs;
    if (seq !== null) {
      seqHigh = null;
      seqLow = null;
    }
  }
  if (seq !== null) {
    if (seq > 2147483647) {
      seq = 2147483647;
    }
    seqHigh = seq >>> 19 & 4095;
    seqLow = seq & 524287;
  }
  if (seqHigh === null || seqLow === null) {
    seqHigh = rnds[6] & 127;
    seqHigh = seqHigh << 8 | rnds[7];
    seqLow = rnds[8] & 63;
    seqLow = seqLow << 8 | rnds[9];
    seqLow = seqLow << 5 | rnds[10] >>> 3;
  }
  if (msecs + 1e4 > _msecs && seq === null) {
    if (++seqLow > 524287) {
      seqLow = 0;
      if (++seqHigh > 4095) {
        seqHigh = 0;
        _msecs++;
      }
    }
  } else {
    _msecs = msecs;
  }
  _seqHigh = seqHigh;
  _seqLow = seqLow;
  b[i++] = _msecs / 1099511627776 & 255;
  b[i++] = _msecs / 4294967296 & 255;
  b[i++] = _msecs / 16777216 & 255;
  b[i++] = _msecs / 65536 & 255;
  b[i++] = _msecs / 256 & 255;
  b[i++] = _msecs & 255;
  b[i++] = seqHigh >>> 4 & 15 | 112;
  b[i++] = seqHigh & 255;
  b[i++] = seqLow >>> 13 & 63 | 128;
  b[i++] = seqLow >>> 5 & 255;
  b[i++] = seqLow << 3 & 255 | rnds[10] & 7;
  b[i++] = rnds[11];
  b[i++] = rnds[12];
  b[i++] = rnds[13];
  b[i++] = rnds[14];
  b[i++] = rnds[15];
  return buf || unsafeStringify(b);
}
var v7_default = v7;

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/experimental/otel/constants.js
var GEN_AI_OPERATION_NAME = "gen_ai.operation.name";
var GEN_AI_SYSTEM = "gen_ai.system";
var GEN_AI_REQUEST_MODEL = "gen_ai.request.model";
var GEN_AI_RESPONSE_MODEL = "gen_ai.response.model";
var GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens";
var GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens";
var GEN_AI_USAGE_TOTAL_TOKENS = "gen_ai.usage.total_tokens";
var GEN_AI_REQUEST_MAX_TOKENS = "gen_ai.request.max_tokens";
var GEN_AI_REQUEST_TEMPERATURE = "gen_ai.request.temperature";
var GEN_AI_REQUEST_TOP_P = "gen_ai.request.top_p";
var GEN_AI_REQUEST_FREQUENCY_PENALTY = "gen_ai.request.frequency_penalty";
var GEN_AI_REQUEST_PRESENCE_PENALTY = "gen_ai.request.presence_penalty";
var GEN_AI_RESPONSE_FINISH_REASONS = "gen_ai.response.finish_reasons";
var GENAI_PROMPT = "gen_ai.prompt";
var GENAI_COMPLETION = "gen_ai.completion";
var GEN_AI_REQUEST_EXTRA_QUERY = "gen_ai.request.extra_query";
var GEN_AI_REQUEST_EXTRA_BODY = "gen_ai.request.extra_body";
var GEN_AI_SERIALIZED_NAME = "gen_ai.serialized.name";
var GEN_AI_SERIALIZED_SIGNATURE = "gen_ai.serialized.signature";
var GEN_AI_SERIALIZED_DOC = "gen_ai.serialized.doc";
var GEN_AI_RESPONSE_ID = "gen_ai.response.id";
var GEN_AI_RESPONSE_SERVICE_TIER = "gen_ai.response.service_tier";
var GEN_AI_RESPONSE_SYSTEM_FINGERPRINT = "gen_ai.response.system_fingerprint";
var GEN_AI_USAGE_INPUT_TOKEN_DETAILS = "gen_ai.usage.input_token_details";
var GEN_AI_USAGE_OUTPUT_TOKEN_DETAILS = "gen_ai.usage.output_token_details";
var LANGSMITH_SESSION_ID = "langsmith.trace.session_id";
var LANGSMITH_SESSION_NAME = "langsmith.trace.session_name";
var LANGSMITH_RUN_TYPE = "langsmith.span.kind";
var LANGSMITH_NAME = "langsmith.trace.name";
var LANGSMITH_METADATA = "langsmith.metadata";
var LANGSMITH_TAGS = "langsmith.span.tags";
var LANGSMITH_REQUEST_STREAMING = "langsmith.request.streaming";
var LANGSMITH_REQUEST_HEADERS = "langsmith.request.headers";

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/env.js
var globalEnv;
var isBrowser = () => typeof window !== "undefined" && typeof window.document !== "undefined";
var isWebWorker = () => typeof globalThis === "object" && globalThis.constructor && globalThis.constructor.name === "DedicatedWorkerGlobalScope";
var isJsDom = () => typeof window !== "undefined" && window.name === "nodejs" || typeof navigator !== "undefined" && navigator.userAgent.includes("jsdom");
var isDeno = () => typeof Deno !== "undefined";
var isNode = () => typeof process !== "undefined" && typeof process.versions !== "undefined" && typeof process.versions.node !== "undefined" && !isDeno();
var getEnv = () => {
  if (globalEnv) {
    return globalEnv;
  }
  if (typeof Bun !== "undefined") {
    globalEnv = "bun";
  } else if (isBrowser()) {
    globalEnv = "browser";
  } else if (isNode()) {
    globalEnv = "node";
  } else if (isWebWorker()) {
    globalEnv = "webworker";
  } else if (isJsDom()) {
    globalEnv = "jsdom";
  } else if (isDeno()) {
    globalEnv = "deno";
  } else {
    globalEnv = "other";
  }
  return globalEnv;
};
var runtimeEnvironment;
function getRuntimeEnvironment() {
  if (runtimeEnvironment === void 0) {
    const env = getEnv();
    const releaseEnv = getShas();
    runtimeEnvironment = {
      library: "langsmith",
      runtime: env,
      sdk: "langsmith-js",
      sdk_version: __version__,
      ...releaseEnv
    };
  }
  return runtimeEnvironment;
}
function getLangSmithEnvVarsMetadata() {
  const allEnvVars = getLangSmithEnvironmentVariables();
  const envVars = {};
  const excluded = [
    "LANGCHAIN_API_KEY",
    "LANGCHAIN_ENDPOINT",
    "LANGCHAIN_TRACING_V2",
    "LANGCHAIN_PROJECT",
    "LANGCHAIN_SESSION",
    "LANGSMITH_API_KEY",
    "LANGSMITH_ENDPOINT",
    "LANGSMITH_TRACING_V2",
    "LANGSMITH_PROJECT",
    "LANGSMITH_SESSION"
  ];
  for (const [key, value] of Object.entries(allEnvVars)) {
    if (typeof value === "string" && !excluded.includes(key) && !key.toLowerCase().includes("key") && !key.toLowerCase().includes("secret") && !key.toLowerCase().includes("token")) {
      if (key === "LANGCHAIN_REVISION_ID") {
        envVars["revision_id"] = value;
      } else {
        envVars[key] = value;
      }
    }
  }
  return envVars;
}
function getLangSmithEnvironmentVariables() {
  const envVars = {};
  try {
    if (typeof process !== "undefined" && process.env) {
      for (const [key, value] of Object.entries(process.env)) {
        if ((key.startsWith("LANGCHAIN_") || key.startsWith("LANGSMITH_")) && value != null) {
          if ((key.toLowerCase().includes("key") || key.toLowerCase().includes("secret") || key.toLowerCase().includes("token")) && typeof value === "string") {
            envVars[key] = value.slice(0, 2) + "*".repeat(value.length - 4) + value.slice(-2);
          } else {
            envVars[key] = value;
          }
        }
      }
    }
  } catch (e) {
  }
  return envVars;
}
function getEnvironmentVariable(name) {
  try {
    return typeof process !== "undefined" ? (
      // eslint-disable-next-line no-process-env
      process.env?.[name]
    ) : void 0;
  } catch (e) {
    return void 0;
  }
}
function getLangSmithEnvironmentVariable(name) {
  return getEnvironmentVariable(`LANGSMITH_${name}`) || getEnvironmentVariable(`LANGCHAIN_${name}`);
}
var cachedCommitSHAs;
function getShas() {
  if (cachedCommitSHAs !== void 0) {
    return cachedCommitSHAs;
  }
  const common_release_envs = [
    "VERCEL_GIT_COMMIT_SHA",
    "NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA",
    "COMMIT_REF",
    "RENDER_GIT_COMMIT",
    "CI_COMMIT_SHA",
    "CIRCLE_SHA1",
    "CF_PAGES_COMMIT_SHA",
    "REACT_APP_GIT_SHA",
    "SOURCE_VERSION",
    "GITHUB_SHA",
    "TRAVIS_COMMIT",
    "GIT_COMMIT",
    "BUILD_VCS_NUMBER",
    "bamboo_planRepository_revision",
    "Build.SourceVersion",
    "BITBUCKET_COMMIT",
    "DRONE_COMMIT_SHA",
    "SEMAPHORE_GIT_SHA",
    "BUILDKITE_COMMIT"
  ];
  const shas = {};
  for (const env of common_release_envs) {
    const envVar = getEnvironmentVariable(env);
    if (envVar !== void 0) {
      shas[env] = envVar;
    }
  }
  cachedCommitSHAs = shas;
  return shas;
}
function getOtelEnabled() {
  return getEnvironmentVariable("OTEL_ENABLED") === "true" || getLangSmithEnvironmentVariable("OTEL_ENABLED") === "true";
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/singletons/otel.js
var MockTracer = class {
  constructor() {
    Object.defineProperty(this, "hasWarned", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: false
    });
  }
  startActiveSpan(_name, ...args) {
    if (!this.hasWarned && getOtelEnabled()) {
      console.warn('You have enabled OTEL export via the `OTEL_ENABLED` or `LANGSMITH_OTEL_ENABLED` environment variable, but have not initialized the required OTEL instances. Please add:\n```\nimport { initializeOTEL } from "langsmith/experimental/otel/setup";\ninitializeOTEL();\n```\nat the beginning of your code.');
      this.hasWarned = true;
    }
    let fn;
    if (args.length === 1 && typeof args[0] === "function") {
      fn = args[0];
    } else if (args.length === 2 && typeof args[1] === "function") {
      fn = args[1];
    } else if (args.length === 3 && typeof args[2] === "function") {
      fn = args[2];
    }
    if (typeof fn === "function") {
      return fn();
    }
    return void 0;
  }
};
var MockOTELTrace = class {
  constructor() {
    Object.defineProperty(this, "mockTracer", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: new MockTracer()
    });
  }
  getTracer(_name, _version) {
    return this.mockTracer;
  }
  getActiveSpan() {
    return void 0;
  }
  setSpan(context, _span) {
    return context;
  }
  getSpan(_context) {
    return void 0;
  }
  setSpanContext(context, _spanContext) {
    return context;
  }
  getTracerProvider() {
    return void 0;
  }
  setGlobalTracerProvider(_tracerProvider) {
    return false;
  }
};
var MockOTELContext = class {
  active() {
    return {};
  }
  with(_context, fn) {
    return fn();
  }
};
var OTEL_TRACE_KEY = /* @__PURE__ */ Symbol.for("ls:otel_trace");
var OTEL_CONTEXT_KEY = /* @__PURE__ */ Symbol.for("ls:otel_context");
var OTEL_GET_DEFAULT_OTLP_TRACER_PROVIDER_KEY = /* @__PURE__ */ Symbol.for("ls:otel_get_default_otlp_tracer_provider");
var mockOTELTrace = new MockOTELTrace();
var mockOTELContext = new MockOTELContext();
var OTELProvider = class {
  getTraceInstance() {
    return globalThis[OTEL_TRACE_KEY] ?? mockOTELTrace;
  }
  getContextInstance() {
    return globalThis[OTEL_CONTEXT_KEY] ?? mockOTELContext;
  }
  initializeGlobalInstances(otel) {
    if (globalThis[OTEL_TRACE_KEY] === void 0) {
      globalThis[OTEL_TRACE_KEY] = otel.trace;
    }
    if (globalThis[OTEL_CONTEXT_KEY] === void 0) {
      globalThis[OTEL_CONTEXT_KEY] = otel.context;
    }
  }
  setDefaultOTLPTracerComponents(components) {
    globalThis[OTEL_GET_DEFAULT_OTLP_TRACER_PROVIDER_KEY] = components;
  }
  getDefaultOTLPTracerComponents() {
    return globalThis[OTEL_GET_DEFAULT_OTLP_TRACER_PROVIDER_KEY] ?? void 0;
  }
};
var OTELProviderSingleton = new OTELProvider();
function getOTELTrace() {
  return OTELProviderSingleton.getTraceInstance();
}
function getOTELContext() {
  return OTELProviderSingleton.getContextInstance();
}
function getDefaultOTLPTracerComponents() {
  return OTELProviderSingleton.getDefaultOTLPTracerComponents();
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/experimental/otel/translator.js
var WELL_KNOWN_OPERATION_NAMES = {
  llm: "chat",
  tool: "execute_tool",
  retriever: "embeddings",
  embedding: "embeddings",
  prompt: "chat"
};
function getOperationName(runType) {
  return WELL_KNOWN_OPERATION_NAMES[runType] || runType;
}
var LangSmithToOTELTranslator = class {
  constructor() {
    Object.defineProperty(this, "spans", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: /* @__PURE__ */ new Map()
    });
  }
  exportBatch(operations, otelContextMap) {
    for (const op of operations) {
      try {
        if (!op.run) {
          continue;
        }
        if (op.operation === "post") {
          const span = this.createSpanForRun(op, op.run, otelContextMap.get(op.id));
          if (span && !op.run.end_time) {
            this.spans.set(op.id, span);
          }
        } else {
          this.updateSpanForRun(op, op.run);
        }
      } catch (e) {
        console.error(`Error processing operation ${op.id}:`, e);
      }
    }
  }
  createSpanForRun(op, runInfo, otelContext) {
    const activeSpan = otelContext && getOTELTrace().getSpan(otelContext);
    if (!activeSpan) {
      return;
    }
    try {
      return this.finishSpanSetup(activeSpan, runInfo, op);
    } catch (e) {
      console.error(`Failed to create span for run ${op.id}:`, e);
      return void 0;
    }
  }
  finishSpanSetup(span, runInfo, op) {
    this.setSpanAttributes(span, runInfo, op);
    if (runInfo.error) {
      span.setStatus({ code: 2 });
      span.recordException(new Error(runInfo.error));
    } else {
      span.setStatus({ code: 1 });
    }
    if (runInfo.end_time) {
      span.end(new Date(runInfo.end_time));
    }
    return span;
  }
  updateSpanForRun(op, runInfo) {
    try {
      const span = this.spans.get(op.id);
      if (!span) {
        console.debug(`No span found for run ${op.id} during update`);
        return;
      }
      this.setSpanAttributes(span, runInfo, op);
      if (runInfo.error) {
        span.setStatus({ code: 2 });
        span.recordException(new Error(runInfo.error));
      } else {
        span.setStatus({ code: 1 });
      }
      const endTime = runInfo.end_time;
      if (endTime) {
        span.end(new Date(endTime));
        this.spans.delete(op.id);
      }
    } catch (e) {
      console.error(`Failed to update span for run ${op.id}:`, e);
    }
  }
  extractModelName(runInfo) {
    if (runInfo.extra?.metadata) {
      const metadata = runInfo.extra.metadata;
      if (metadata.ls_model_name) {
        return metadata.ls_model_name;
      }
      if (metadata.invocation_params) {
        const invocationParams = metadata.invocation_params;
        if (invocationParams.model) {
          return invocationParams.model;
        } else if (invocationParams.model_name) {
          return invocationParams.model_name;
        }
      }
    }
    return;
  }
  setSpanAttributes(span, runInfo, op) {
    if ("run_type" in runInfo && runInfo.run_type) {
      span.setAttribute(LANGSMITH_RUN_TYPE, runInfo.run_type);
      const operationName = getOperationName(runInfo.run_type || "chain");
      span.setAttribute(GEN_AI_OPERATION_NAME, operationName);
    }
    if ("name" in runInfo && runInfo.name) {
      span.setAttribute(LANGSMITH_NAME, runInfo.name);
    }
    if ("session_id" in runInfo && runInfo.session_id) {
      span.setAttribute(LANGSMITH_SESSION_ID, runInfo.session_id);
    }
    if ("session_name" in runInfo && runInfo.session_name) {
      span.setAttribute(LANGSMITH_SESSION_NAME, runInfo.session_name);
    }
    this.setGenAiSystem(span, runInfo);
    const modelName = this.extractModelName(runInfo);
    if (modelName) {
      span.setAttribute(GEN_AI_REQUEST_MODEL, modelName);
    }
    if ("prompt_tokens" in runInfo && typeof runInfo.prompt_tokens === "number") {
      span.setAttribute(GEN_AI_USAGE_INPUT_TOKENS, runInfo.prompt_tokens);
    }
    if ("completion_tokens" in runInfo && typeof runInfo.completion_tokens === "number") {
      span.setAttribute(GEN_AI_USAGE_OUTPUT_TOKENS, runInfo.completion_tokens);
    }
    if ("total_tokens" in runInfo && typeof runInfo.total_tokens === "number") {
      span.setAttribute(GEN_AI_USAGE_TOTAL_TOKENS, runInfo.total_tokens);
    }
    this.setInvocationParameters(span, runInfo);
    const metadata = runInfo.extra?.metadata || {};
    for (const [key, value] of Object.entries(metadata)) {
      if (value !== null && value !== void 0) {
        span.setAttribute(`${LANGSMITH_METADATA}.${key}`, String(value));
      }
    }
    const tags = runInfo.tags;
    if (tags && Array.isArray(tags)) {
      span.setAttribute(LANGSMITH_TAGS, tags.join(", "));
    } else if (tags) {
      span.setAttribute(LANGSMITH_TAGS, String(tags));
    }
    if ("serialized" in runInfo && typeof runInfo.serialized === "object") {
      const serialized = runInfo.serialized;
      if (serialized.name) {
        span.setAttribute(GEN_AI_SERIALIZED_NAME, String(serialized.name));
      }
      if (serialized.signature) {
        span.setAttribute(GEN_AI_SERIALIZED_SIGNATURE, String(serialized.signature));
      }
      if (serialized.doc) {
        span.setAttribute(GEN_AI_SERIALIZED_DOC, String(serialized.doc));
      }
    }
    this.setIOAttributes(span, op);
  }
  setGenAiSystem(span, runInfo) {
    let system = "langchain";
    const modelName = this.extractModelName(runInfo);
    if (modelName) {
      const modelLower = modelName.toLowerCase();
      if (modelLower.includes("anthropic") || modelLower.startsWith("claude")) {
        system = "anthropic";
      } else if (modelLower.includes("bedrock")) {
        system = "aws.bedrock";
      } else if (modelLower.includes("azure") && modelLower.includes("openai")) {
        system = "az.ai.openai";
      } else if (modelLower.includes("azure") && modelLower.includes("inference")) {
        system = "az.ai.inference";
      } else if (modelLower.includes("cohere")) {
        system = "cohere";
      } else if (modelLower.includes("deepseek")) {
        system = "deepseek";
      } else if (modelLower.includes("gemini")) {
        system = "gemini";
      } else if (modelLower.includes("groq")) {
        system = "groq";
      } else if (modelLower.includes("watson") || modelLower.includes("ibm")) {
        system = "ibm.watsonx.ai";
      } else if (modelLower.includes("mistral")) {
        system = "mistral_ai";
      } else if (modelLower.includes("gpt") || modelLower.includes("openai")) {
        system = "openai";
      } else if (modelLower.includes("perplexity") || modelLower.includes("sonar")) {
        system = "perplexity";
      } else if (modelLower.includes("vertex")) {
        system = "vertex_ai";
      } else if (modelLower.includes("xai") || modelLower.includes("grok")) {
        system = "xai";
      }
    }
    span.setAttribute(GEN_AI_SYSTEM, system);
  }
  setInvocationParameters(span, runInfo) {
    if (!runInfo.extra?.metadata?.invocation_params) {
      return;
    }
    const invocationParams = runInfo.extra.metadata.invocation_params;
    if (invocationParams.max_tokens !== void 0) {
      span.setAttribute(GEN_AI_REQUEST_MAX_TOKENS, invocationParams.max_tokens);
    }
    if (invocationParams.temperature !== void 0) {
      span.setAttribute(GEN_AI_REQUEST_TEMPERATURE, invocationParams.temperature);
    }
    if (invocationParams.top_p !== void 0) {
      span.setAttribute(GEN_AI_REQUEST_TOP_P, invocationParams.top_p);
    }
    if (invocationParams.frequency_penalty !== void 0) {
      span.setAttribute(GEN_AI_REQUEST_FREQUENCY_PENALTY, invocationParams.frequency_penalty);
    }
    if (invocationParams.presence_penalty !== void 0) {
      span.setAttribute(GEN_AI_REQUEST_PRESENCE_PENALTY, invocationParams.presence_penalty);
    }
  }
  setIOAttributes(span, op) {
    if (op.run.inputs) {
      try {
        const inputs = op.run.inputs;
        if (typeof inputs === "object" && inputs !== null) {
          if (inputs.model && Array.isArray(inputs.messages)) {
            span.setAttribute(GEN_AI_REQUEST_MODEL, inputs.model);
          }
          if (inputs.stream !== void 0) {
            span.setAttribute(LANGSMITH_REQUEST_STREAMING, inputs.stream);
          }
          if (inputs.extra_headers) {
            span.setAttribute(LANGSMITH_REQUEST_HEADERS, JSON.stringify(inputs.extra_headers));
          }
          if (inputs.extra_query) {
            span.setAttribute(GEN_AI_REQUEST_EXTRA_QUERY, JSON.stringify(inputs.extra_query));
          }
          if (inputs.extra_body) {
            span.setAttribute(GEN_AI_REQUEST_EXTRA_BODY, JSON.stringify(inputs.extra_body));
          }
        }
        span.setAttribute(GENAI_PROMPT, JSON.stringify(inputs));
      } catch (e) {
        console.debug(`Failed to process inputs for run ${op.id}`, e);
      }
    }
    if (op.run.outputs) {
      try {
        const outputs = op.run.outputs;
        const tokenUsage = this.getUnifiedRunTokens(outputs);
        if (tokenUsage) {
          span.setAttribute(GEN_AI_USAGE_INPUT_TOKENS, tokenUsage[0]);
          span.setAttribute(GEN_AI_USAGE_OUTPUT_TOKENS, tokenUsage[1]);
          span.setAttribute(GEN_AI_USAGE_TOTAL_TOKENS, tokenUsage[0] + tokenUsage[1]);
        }
        if (outputs && typeof outputs === "object") {
          if (outputs.model) {
            span.setAttribute(GEN_AI_RESPONSE_MODEL, String(outputs.model));
          }
          if (outputs.id) {
            span.setAttribute(GEN_AI_RESPONSE_ID, outputs.id);
          }
          if (outputs.choices && Array.isArray(outputs.choices)) {
            const finishReasons = outputs.choices.map((choice) => choice.finish_reason).filter((reason) => reason).map(String);
            if (finishReasons.length > 0) {
              span.setAttribute(GEN_AI_RESPONSE_FINISH_REASONS, finishReasons.join(", "));
            }
          }
          if (outputs.service_tier) {
            span.setAttribute(GEN_AI_RESPONSE_SERVICE_TIER, outputs.service_tier);
          }
          if (outputs.system_fingerprint) {
            span.setAttribute(GEN_AI_RESPONSE_SYSTEM_FINGERPRINT, outputs.system_fingerprint);
          }
          if (outputs.usage_metadata && typeof outputs.usage_metadata === "object") {
            const usageMetadata = outputs.usage_metadata;
            if (usageMetadata.input_token_details) {
              span.setAttribute(GEN_AI_USAGE_INPUT_TOKEN_DETAILS, JSON.stringify(usageMetadata.input_token_details));
            }
            if (usageMetadata.output_token_details) {
              span.setAttribute(GEN_AI_USAGE_OUTPUT_TOKEN_DETAILS, JSON.stringify(usageMetadata.output_token_details));
            }
          }
        }
        span.setAttribute(GENAI_COMPLETION, JSON.stringify(outputs));
      } catch (e) {
        console.debug(`Failed to process outputs for run ${op.id}`, e);
      }
    }
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  getUnifiedRunTokens(outputs) {
    if (!outputs) {
      return null;
    }
    let tokenUsage = this.extractUnifiedRunTokens(outputs.usage_metadata);
    if (tokenUsage) {
      return tokenUsage;
    }
    const keys = Object.keys(outputs);
    for (const key of keys) {
      const haystack = outputs[key];
      if (!haystack || typeof haystack !== "object") {
        continue;
      }
      tokenUsage = this.extractUnifiedRunTokens(haystack.usage_metadata);
      if (tokenUsage) {
        return tokenUsage;
      }
      if (haystack.lc === 1 && haystack.kwargs && typeof haystack.kwargs === "object") {
        tokenUsage = this.extractUnifiedRunTokens(haystack.kwargs.usage_metadata);
        if (tokenUsage) {
          return tokenUsage;
        }
      }
    }
    const generations = outputs.generations || [];
    if (!Array.isArray(generations)) {
      return null;
    }
    const flatGenerations = Array.isArray(generations[0]) ? generations.flat() : generations;
    for (const generation of flatGenerations) {
      if (typeof generation === "object" && generation.message && typeof generation.message === "object" && generation.message.kwargs && typeof generation.message.kwargs === "object") {
        tokenUsage = this.extractUnifiedRunTokens(generation.message.kwargs.usage_metadata);
        if (tokenUsage) {
          return tokenUsage;
        }
      }
    }
    return null;
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  extractUnifiedRunTokens(outputs) {
    if (!outputs || typeof outputs !== "object") {
      return null;
    }
    if (typeof outputs.input_tokens !== "number" || typeof outputs.output_tokens !== "number") {
      return null;
    }
    return [outputs.input_tokens, outputs.output_tokens];
  }
};

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/is-network-error/index.js
var objectToString = Object.prototype.toString;
var isError = (value) => objectToString.call(value) === "[object Error]";
var errorMessages = /* @__PURE__ */ new Set([
  "network error",
  // Chrome
  "Failed to fetch",
  // Chrome
  "NetworkError when attempting to fetch resource.",
  // Firefox
  "The Internet connection appears to be offline.",
  // Safari 16
  "Network request failed",
  // `cross-fetch`
  "fetch failed",
  // Undici (Node.js)
  "terminated",
  // Undici (Node.js)
  " A network error occurred.",
  // Bun (WebKit)
  "Network connection lost"
  // Cloudflare Workers (fetch)
]);
function isNetworkError(error2) {
  const isValid = error2 && isError(error2) && error2.name === "TypeError" && typeof error2.message === "string";
  if (!isValid) {
    return false;
  }
  const { message, stack } = error2;
  if (message === "Load failed") {
    return stack === void 0 || // Sentry adds its own stack trace to the fetch error, so also check for that
    "__sentry_captured__" in error2;
  }
  if (message.startsWith("error sending request for url")) {
    return true;
  }
  return errorMessages.has(message);
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/p-retry/index.js
function validateRetries(retries) {
  if (typeof retries === "number") {
    if (retries < 0) {
      throw new TypeError("Expected `retries` to be a non-negative number.");
    }
    if (Number.isNaN(retries)) {
      throw new TypeError("Expected `retries` to be a valid number or Infinity, got NaN.");
    }
  } else if (retries !== void 0) {
    throw new TypeError("Expected `retries` to be a number or Infinity.");
  }
}
function validateNumberOption(name, value, { min = 0, allowInfinity = false } = {}) {
  if (value === void 0) {
    return;
  }
  if (typeof value !== "number" || Number.isNaN(value)) {
    throw new TypeError(`Expected \`${name}\` to be a number${allowInfinity ? " or Infinity" : ""}.`);
  }
  if (!allowInfinity && !Number.isFinite(value)) {
    throw new TypeError(`Expected \`${name}\` to be a finite number.`);
  }
  if (value < min) {
    throw new TypeError(`Expected \`${name}\` to be \u2265 ${min}.`);
  }
}
var AbortError = class extends Error {
  constructor(message) {
    super();
    if (message instanceof Error) {
      this.originalError = message;
      ({ message } = message);
    } else {
      this.originalError = new Error(message);
      this.originalError.stack = this.stack;
    }
    this.name = "AbortError";
    this.message = message;
  }
};
function calculateDelay(retriesConsumed, options) {
  const attempt = Math.max(1, retriesConsumed + 1);
  const random = options.randomize ? Math.random() + 1 : 1;
  let timeout = Math.round(random * options.minTimeout * options.factor ** (attempt - 1));
  timeout = Math.min(timeout, options.maxTimeout);
  return timeout;
}
function calculateRemainingTime(start, max) {
  if (!Number.isFinite(max)) {
    return max;
  }
  return max - (performance.now() - start);
}
async function onAttemptFailure({ error: error2, attemptNumber, retriesConsumed, startTime, options }) {
  const normalizedError = error2 instanceof Error ? error2 : new TypeError(`Non-error was thrown: "${error2}". You should only throw errors.`);
  if (normalizedError instanceof AbortError) {
    throw normalizedError.originalError;
  }
  const retriesLeft = Number.isFinite(options.retries) ? Math.max(0, options.retries - retriesConsumed) : options.retries;
  const maxRetryTime = options.maxRetryTime ?? Number.POSITIVE_INFINITY;
  const context = Object.freeze({
    error: normalizedError,
    attemptNumber,
    retriesLeft,
    retriesConsumed
  });
  await options.onFailedAttempt(context);
  if (calculateRemainingTime(startTime, maxRetryTime) <= 0) {
    throw normalizedError;
  }
  const consumeRetry = await options.shouldConsumeRetry(context);
  const remainingTime = calculateRemainingTime(startTime, maxRetryTime);
  if (remainingTime <= 0 || retriesLeft <= 0) {
    throw normalizedError;
  }
  if (normalizedError instanceof TypeError && !isNetworkError(normalizedError)) {
    if (consumeRetry) {
      throw normalizedError;
    }
    options.signal?.throwIfAborted();
    return false;
  }
  if (!await options.shouldRetry(context)) {
    throw normalizedError;
  }
  if (!consumeRetry) {
    options.signal?.throwIfAborted();
    return false;
  }
  const delayTime = calculateDelay(retriesConsumed, options);
  const finalDelay = Math.min(delayTime, remainingTime);
  if (finalDelay > 0) {
    await new Promise((resolve, reject) => {
      const onAbort = () => {
        clearTimeout(timeoutToken);
        options.signal?.removeEventListener("abort", onAbort);
        reject(options.signal.reason);
      };
      const timeoutToken = setTimeout(() => {
        options.signal?.removeEventListener("abort", onAbort);
        resolve();
      }, finalDelay);
      if (options.unref) {
        timeoutToken.unref?.();
      }
      options.signal?.addEventListener("abort", onAbort, { once: true });
    });
  }
  options.signal?.throwIfAborted();
  return true;
}
async function pRetry(input, options = {}) {
  options = { ...options };
  validateRetries(options.retries);
  if (Object.hasOwn(options, "forever")) {
    throw new Error("The `forever` option is no longer supported. For many use-cases, you can set `retries: Infinity` instead.");
  }
  options.retries ??= 10;
  options.factor ??= 2;
  options.minTimeout ??= 1e3;
  options.maxTimeout ??= Number.POSITIVE_INFINITY;
  options.maxRetryTime ??= Number.POSITIVE_INFINITY;
  options.randomize ??= false;
  options.onFailedAttempt ??= () => {
  };
  options.shouldRetry ??= () => true;
  options.shouldConsumeRetry ??= () => true;
  validateNumberOption("factor", options.factor, {
    min: 0,
    allowInfinity: false
  });
  validateNumberOption("minTimeout", options.minTimeout, {
    min: 0,
    allowInfinity: false
  });
  validateNumberOption("maxTimeout", options.maxTimeout, {
    min: 0,
    allowInfinity: true
  });
  validateNumberOption("maxRetryTime", options.maxRetryTime, {
    min: 0,
    allowInfinity: true
  });
  if (!(options.factor > 0)) {
    options.factor = 1;
  }
  options.signal?.throwIfAborted();
  let attemptNumber = 0;
  let retriesConsumed = 0;
  const startTime = performance.now();
  while (Number.isFinite(options.retries) ? retriesConsumed <= options.retries : true) {
    attemptNumber++;
    try {
      options.signal?.throwIfAborted();
      const result = await input(attemptNumber);
      options.signal?.throwIfAborted();
      return result;
    } catch (error2) {
      if (await onAttemptFailure({
        error: error2,
        attemptNumber,
        retriesConsumed,
        startTime,
        options
      })) {
        retriesConsumed++;
      }
    }
  }
  throw new Error("Retry attempts exhausted without throwing an error.");
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/p-queue.js
var import_p_queue = __toESM(require_dist(), 1);
var PQueue = "default" in import_p_queue.default ? import_p_queue.default.default : import_p_queue.default;

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/async_caller.js
var STATUS_RETRYABLE = [
  408,
  // Request Timeout
  425,
  // Too Early
  429,
  // Too Many Requests
  500,
  // Internal Server Error
  502,
  // Bad Gateway
  503,
  // Service Unavailable
  504
  // Gateway Timeout
];
var AsyncCaller = class {
  constructor(params) {
    Object.defineProperty(this, "maxConcurrency", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "maxRetries", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "maxQueueSizeBytes", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "queue", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "onFailedResponseHook", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "queueSizeBytes", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: 0
    });
    this.maxConcurrency = params.maxConcurrency ?? Infinity;
    this.maxRetries = params.maxRetries ?? 6;
    this.maxQueueSizeBytes = params.maxQueueSizeBytes;
    this.queue = new PQueue({ concurrency: this.maxConcurrency });
    this.onFailedResponseHook = params?.onFailedResponseHook;
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  call(callable, ...args) {
    return this.callWithOptions({}, callable, ...args);
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  callWithOptions(options, callable, ...args) {
    const sizeBytes = options.sizeBytes ?? 0;
    if (this.maxQueueSizeBytes !== void 0 && sizeBytes > 0 && this.queueSizeBytes + sizeBytes > this.maxQueueSizeBytes) {
      return Promise.reject(new Error(`Queue size limit (${this.maxQueueSizeBytes} bytes) exceeded. Current queue size: ${this.queueSizeBytes} bytes, attempted addition: ${sizeBytes} bytes.`));
    }
    if (sizeBytes > 0) {
      this.queueSizeBytes += sizeBytes;
    }
    const onFailedResponseHook = this.onFailedResponseHook;
    let promise = this.queue.add(() => pRetry(() => callable(...args).catch((error2) => {
      if (error2 instanceof Error) {
        throw error2;
      } else {
        throw new Error(error2);
      }
    }), {
      async onFailedAttempt({ error: error2 }) {
        if (typeof error2 !== "object" || error2 == null)
          throw error2;
        const errorMessage = "message" in error2 && typeof error2.message === "string" ? error2.message : void 0;
        if (errorMessage?.startsWith("Cancel") || errorMessage?.startsWith("TimeoutError") || errorMessage?.startsWith("AbortError")) {
          throw error2;
        }
        if ("name" in error2 && error2.name === "TimeoutError") {
          throw error2;
        }
        if ("code" in error2 && error2.code === "ECONNABORTED") {
          throw error2;
        }
        const response = "response" in error2 ? error2.response : void 0;
        if (onFailedResponseHook) {
          const handled = await onFailedResponseHook(response);
          if (handled)
            return;
        }
        const status = response?.status ?? ("status" in error2 ? error2.status : void 0);
        if (status != null && (typeof status === "number" || typeof status === "string") && !STATUS_RETRYABLE.includes(+status)) {
          throw error2;
        }
      },
      retries: this.maxRetries,
      randomize: true
    }), { throwOnTimeout: true });
    if (sizeBytes > 0) {
      promise = promise.finally(() => {
        this.queueSizeBytes -= sizeBytes;
      });
    }
    if (options.signal) {
      return Promise.race([
        promise,
        new Promise((_, reject) => {
          options.signal?.addEventListener("abort", () => {
            reject(new Error("AbortError"));
          });
        })
      ]);
    }
    return promise;
  }
};

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/messages.js
function isLangChainMessage(message) {
  return typeof message?._getType === "function";
}
function convertLangChainMessageToExample(message) {
  const converted = {
    type: message._getType(),
    data: { content: message.content }
  };
  if (message?.additional_kwargs && Object.keys(message.additional_kwargs).length > 0) {
    converted.data.additional_kwargs = { ...message.additional_kwargs };
  }
  return converted;
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/warn.js
var warnedMessages = {};
function warnOnce(message) {
  if (!warnedMessages[message]) {
    console.warn(message);
    warnedMessages[message] = true;
  }
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/xxhash/xxhash.js
var n = (n2) => BigInt(n2);
var PRIME32_1 = n("0x9E3779B1");
var PRIME32_2 = n("0x85EBCA77");
var PRIME32_3 = n("0xC2B2AE3D");
var PRIME64_1 = n("0x9E3779B185EBCA87");
var PRIME64_2 = n("0xC2B2AE3D27D4EB4F");
var PRIME64_3 = n("0x165667B19E3779F9");
var PRIME64_4 = n("0x85EBCA77C2B2AE63");
var PRIME64_5 = n("0x27D4EB2F165667C5");
var PRIME_MX1 = n("0x165667919E3779F9");
var PRIME_MX2 = n("0x9FB21C651E98DF25");
function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
}
var kkey = hexToBytes("b8fe6c3923a44bbe7c01812cf721ad1cded46de9839097db7240a4a4b7b3671fcb79e64eccc0e578825ad07dccff7221b8084674f743248ee03590e6813a264c3c2852bb91c300cb88d0658b1b532ea371644897a20df94e3819ef46a9deacd8a8fa763fe39c343ff9dcbbc7c70b4f1d8a51e04bcdb45931c89f7ec9d9787364eac5ac8334d3ebc3c581a0fffa1363eb170ddd51b7f0da49d316552629d4689e2b16be587d47a1fc8ff8b8d17ad031ce45cb3a8f95160428afd7fbcabb4b407e");
var mask128 = (n(1) << n(128)) - n(1);
var mask64 = (n(1) << n(64)) - n(1);
var mask32 = (n(1) << n(32)) - n(1);
var STRIPE_LEN = 64;
var ACC_NB = STRIPE_LEN / 8;
var _U64 = 8;
var _U32 = 4;
function getView(buf, offset = 0) {
  return new Uint8Array(buf.buffer, buf.byteOffset + offset, buf.length - offset);
}
function readBigUInt64LE(buf, offset = 0) {
  const view = new DataView(buf.buffer, buf.byteOffset + offset);
  return view.getBigUint64(0, true);
}
function readUInt32LE(buf, offset = 0) {
  const view = new DataView(buf.buffer, buf.byteOffset + offset);
  return view.getUint32(0, true);
}
function readUInt8(buf, offset = 0) {
  return buf[offset];
}
var bswap64 = (a) => {
  return (a & n(255)) << n(56) | (a & n(65280)) << n(40) | (a & n(16711680)) << n(24) | (a & n(4278190080)) << n(8) | (a & n(1095216660480)) >> n(8) | (a & n(280375465082880)) >> n(24) | (a & n(71776119061217280)) >> n(40) | (a & n(18374686479671624e3)) >> n(56);
};
var bswap32 = (a) => {
  a = (a & n(65535)) << n(16) | (a & n(4294901760)) >> n(16);
  a = (a & n(16711935)) << n(8) | (a & n(4278255360)) >> n(8);
  return a;
};
var XXH_mult32to64 = (a, b) => (a & mask32) * (b & mask32) & mask64;
var assert = (a) => {
  if (!a)
    throw new Error("Assert failed");
};
function rotl32(a, b) {
  return (a << b | a >> n(32) - b) & mask32;
}
function XXH3_accumulate_512(acc, data, key) {
  for (let i = 0; i < ACC_NB; i++) {
    const data_val = readBigUInt64LE(data, i * 8);
    const data_key = data_val ^ readBigUInt64LE(key, i * 8);
    acc[i ^ 1] += data_val;
    acc[i] += XXH_mult32to64(data_key, data_key >> n(32));
  }
  return acc;
}
function XXH3_accumulate(acc, data, key, nbStripes) {
  for (let n2 = 0; n2 < nbStripes; n2++) {
    XXH3_accumulate_512(acc, getView(data, n2 * STRIPE_LEN), getView(key, n2 * 8));
  }
  return acc;
}
function XXH3_scrambleAcc(acc, key) {
  for (let i = 0; i < ACC_NB; i++) {
    const key64 = readBigUInt64LE(key, i * 8);
    let acc64 = acc[i];
    acc64 = xorshift64(acc64, n(47));
    acc64 ^= key64;
    acc64 *= PRIME32_1;
    acc[i] = acc64 & mask64;
  }
  return acc;
}
function XXH3_mix2Accs(acc, key) {
  return XXH3_mul128_fold64(acc[0] ^ readBigUInt64LE(key, 0), acc[1] ^ readBigUInt64LE(key, _U64));
}
function XXH3_mergeAccs(acc, key, start) {
  let result64 = start;
  result64 += XXH3_mix2Accs(acc.slice(0), getView(key, 0 * _U32));
  result64 += XXH3_mix2Accs(acc.slice(2), getView(key, 4 * _U32));
  result64 += XXH3_mix2Accs(acc.slice(4), getView(key, 8 * _U32));
  result64 += XXH3_mix2Accs(acc.slice(6), getView(key, 12 * _U32));
  return XXH3_avalanche(result64 & mask64);
}
function XXH3_hashLong(acc, data, secret, f_acc, f_scramble) {
  const nbStripesPerBlock = Math.floor((secret.byteLength - STRIPE_LEN) / 8);
  const block_len = STRIPE_LEN * nbStripesPerBlock;
  const nb_blocks = Math.floor((data.byteLength - 1) / block_len);
  for (let n2 = 0; n2 < nb_blocks; n2++) {
    acc = XXH3_accumulate(acc, getView(data, n2 * block_len), secret, nbStripesPerBlock);
    acc = f_scramble(acc, getView(secret, secret.byteLength - STRIPE_LEN));
  }
  {
    const nbStripes = Math.floor((data.byteLength - 1 - block_len * nb_blocks) / STRIPE_LEN);
    acc = XXH3_accumulate(acc, getView(data, nb_blocks * block_len), secret, nbStripes);
    acc = f_acc(acc, getView(data, data.byteLength - STRIPE_LEN), getView(secret, secret.byteLength - STRIPE_LEN - 7));
  }
  return acc;
}
function XXH3_hashLong_128b(data, secret, seed) {
  let acc = new BigUint64Array([
    PRIME32_3,
    PRIME64_1,
    PRIME64_2,
    PRIME64_3,
    PRIME64_4,
    PRIME32_2,
    PRIME64_5,
    PRIME32_1
  ]);
  assert(data.length > 128);
  acc = XXH3_hashLong(acc, data, secret, XXH3_accumulate_512, XXH3_scrambleAcc);
  assert(acc.length * 8 == 64);
  {
    const low64 = XXH3_mergeAccs(acc, getView(secret, 11), n(data.byteLength) * PRIME64_1 & mask64);
    const high64 = XXH3_mergeAccs(acc, getView(secret, secret.byteLength - STRIPE_LEN - 11), ~(n(data.byteLength) * PRIME64_2) & mask64);
    return high64 << n(64) | low64;
  }
}
function XXH3_mul128_fold64(a, b) {
  const lll = a * b & mask128;
  return lll & mask64 ^ lll >> n(64);
}
function XXH3_mix16B(data, key, seed) {
  return XXH3_mul128_fold64((readBigUInt64LE(data, 0) ^ readBigUInt64LE(key, 0) + seed) & mask64, (readBigUInt64LE(data, 8) ^ readBigUInt64LE(key, 8) - seed) & mask64);
}
function XXH3_mix32B(acc, data1, data2, key, seed) {
  let accl = acc & mask64;
  let acch = acc >> n(64) & mask64;
  accl += XXH3_mix16B(data1, key, seed);
  accl ^= readBigUInt64LE(data2, 0) + readBigUInt64LE(data2, 8);
  accl &= mask64;
  acch += XXH3_mix16B(data2, getView(key, 16), seed);
  acch ^= readBigUInt64LE(data1, 0) + readBigUInt64LE(data1, 8);
  acch &= mask64;
  return acch << n(64) | accl;
}
function XXH3_avalanche(h64) {
  h64 ^= h64 >> n(37);
  h64 *= PRIME_MX1;
  h64 &= mask64;
  h64 ^= h64 >> n(32);
  return h64;
}
function XXH3_avalanche64(h64) {
  h64 ^= h64 >> n(33);
  h64 *= PRIME64_2;
  h64 &= mask64;
  h64 ^= h64 >> n(29);
  h64 *= PRIME64_3;
  h64 &= mask64;
  h64 ^= h64 >> n(32);
  return h64;
}
function XXH3_len_1to3_128b(data, key32, seed) {
  const len = data.byteLength;
  assert(len > 0 && len <= 3);
  const combined = n(readUInt8(data, len - 1)) | n(len << 8) | n(readUInt8(data, 0) << 16) | n(readUInt8(data, len >> 1) << 24);
  const blow = (n(readUInt32LE(key32, 0)) ^ n(readUInt32LE(key32, 4))) + seed;
  const low = (combined ^ blow) & mask64;
  const bhigh = (n(readUInt32LE(key32, 8)) ^ n(readUInt32LE(key32, 12))) - seed;
  const high = (rotl32(bswap32(combined), n(13)) ^ bhigh) & mask64;
  return (XXH3_avalanche64(high) & mask64) << n(64) | XXH3_avalanche64(low);
}
function xorshift64(b, shift) {
  return b ^ b >> shift;
}
function XXH3_len_4to8_128b(data, key32, seed) {
  const len = data.byteLength;
  assert(len >= 4 && len <= 8);
  {
    const l1 = readUInt32LE(data, 0);
    const l2 = readUInt32LE(data, len - 4);
    const l64 = n(l1) | n(l2) << n(32);
    const bitflip = (readBigUInt64LE(key32, 16) ^ readBigUInt64LE(key32, 24)) + seed & mask64;
    const keyed = l64 ^ bitflip;
    let m128 = keyed * (PRIME64_1 + (n(len) << n(2))) & mask128;
    m128 += (m128 & mask64) << n(65);
    m128 &= mask128;
    m128 ^= m128 >> n(67);
    return xorshift64(xorshift64(m128 & mask64, n(35)) * PRIME_MX2 & mask64, n(28)) | XXH3_avalanche(m128 >> n(64)) << n(64);
  }
}
function XXH3_len_9to16_128b(data, key64, seed) {
  const len = data.byteLength;
  assert(len >= 9 && len <= 16);
  {
    const bitflipl = (readBigUInt64LE(key64, 32) ^ readBigUInt64LE(key64, 40)) + seed & mask64;
    const bitfliph = (readBigUInt64LE(key64, 48) ^ readBigUInt64LE(key64, 56)) - seed & mask64;
    const ll1 = readBigUInt64LE(data);
    let ll2 = readBigUInt64LE(data, len - 8);
    let m128 = (ll1 ^ ll2 ^ bitflipl) * PRIME64_1;
    const m128_l = (m128 & mask64) + (n(len - 1) << n(54));
    m128 = m128 & (mask128 ^ mask64) | m128_l;
    ll2 ^= bitfliph;
    m128 += ll2 + (ll2 & mask32) * (PRIME32_2 - n(1)) << n(64);
    m128 &= mask128;
    m128 ^= bswap64(m128 >> n(64));
    let h128 = (m128 & mask64) * PRIME64_2;
    h128 += (m128 >> n(64)) * PRIME64_2 << n(64);
    h128 &= mask128;
    return XXH3_avalanche(h128 & mask64) | XXH3_avalanche(h128 >> n(64)) << n(64);
  }
}
function XXH3_len_0to16_128b(data, seed) {
  const len = data.byteLength;
  assert(len <= 16);
  if (len > 8)
    return XXH3_len_9to16_128b(data, kkey, seed);
  if (len >= 4)
    return XXH3_len_4to8_128b(data, kkey, seed);
  if (len > 0)
    return XXH3_len_1to3_128b(data, kkey, seed);
  return XXH3_avalanche64(seed ^ readBigUInt64LE(kkey, 64) ^ readBigUInt64LE(kkey, 72)) | XXH3_avalanche64(seed ^ readBigUInt64LE(kkey, 80) ^ readBigUInt64LE(kkey, 88)) << n(64);
}
function inv64(x) {
  return ~x + n(1) & mask64;
}
function XXH3_len_17to128_128b(data, secret, seed) {
  let acc = n(data.byteLength) * PRIME64_1 & mask64;
  let i = n(data.byteLength - 1) / n(32);
  while (i >= 0) {
    const ni = Number(i);
    acc = XXH3_mix32B(acc, getView(data, 16 * ni), getView(data, data.byteLength - 16 * (ni + 1)), getView(secret, 32 * ni), seed);
    i--;
  }
  let h128l = acc + (acc >> n(64)) & mask64;
  h128l = XXH3_avalanche(h128l);
  let h128h = (acc & mask64) * PRIME64_1 + (acc >> n(64)) * PRIME64_4 + (n(data.byteLength) - seed & mask64) * PRIME64_2;
  h128h &= mask64;
  h128h = inv64(XXH3_avalanche(h128h));
  return h128l | h128h << n(64);
}
function XXH3_len_129to240_128b(data, secret, seed) {
  let acc = n(data.byteLength) * PRIME64_1 & mask64;
  for (let i = 32; i < 160; i += 32) {
    acc = XXH3_mix32B(acc, getView(data, i - 32), getView(data, i - 16), getView(secret, i - 32), seed);
  }
  acc = XXH3_avalanche(acc & mask64) | XXH3_avalanche(acc >> n(64)) << n(64);
  for (let i = 160; i <= data.byteLength; i += 32) {
    acc = XXH3_mix32B(acc, getView(data, i - 32), getView(data, i - 16), getView(secret, 3 + i - 160), seed);
  }
  acc = XXH3_mix32B(acc, getView(data, data.byteLength - 16), getView(data, data.byteLength - 32), getView(secret, 136 - 17 - 16), inv64(seed));
  let h128l = acc + (acc >> n(64)) & mask64;
  h128l = XXH3_avalanche(h128l);
  let h128h = (acc & mask64) * PRIME64_1 + (acc >> n(64)) * PRIME64_4 + (n(data.byteLength) - seed & mask64) * PRIME64_2;
  h128h &= mask64;
  h128h = inv64(XXH3_avalanche(h128h));
  return h128l | h128h << n(64);
}
function XXH3_128(data, seed = n(0)) {
  const len = data.byteLength;
  if (len <= 16)
    return XXH3_len_0to16_128b(data, seed);
  if (len <= 128)
    return XXH3_len_17to128_128b(data, kkey, seed);
  if (len <= 240)
    return XXH3_len_129to240_128b(data, kkey, seed);
  return XXH3_hashLong_128b(data, kkey, seed);
}
function xxh128ToBytes(hash128) {
  const result = new Uint8Array(16);
  const view = new DataView(result.buffer);
  const low64 = hash128 & mask64;
  const high64 = hash128 >> n(64);
  view.setBigUint64(0, high64, false);
  view.setBigUint64(8, low64, false);
  return result;
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/_uuid.js
var UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
function assertUuid(str, which) {
  if (!UUID_REGEX.test(str)) {
    const msg = which !== void 0 ? `Invalid UUID for ${which}: ${str}` : `Invalid UUID: ${str}`;
    throw new Error(msg);
  }
  return str;
}
function uuid7FromTime(timestamp) {
  const msecs = typeof timestamp === "string" ? Date.parse(timestamp) : timestamp;
  return v7_default({ msecs, seq: 0 });
}
function getUuidVersion(uuidStr) {
  if (!UUID_REGEX.test(uuidStr)) {
    return null;
  }
  const versionChar = uuidStr[14];
  return parseInt(versionChar, 16);
}
function uuidToBytes(uuidStr) {
  const hex = uuidStr.replace(/-/g, "");
  const bytes = new Uint8Array(16);
  for (let i = 0; i < 16; i++) {
    bytes[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  }
  return bytes;
}
function bytesToUuid(bytes) {
  const hex = Array.from(bytes).map((b) => b.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
var _textEncoder = new TextEncoder();
function _fastHash128(str) {
  const data = _textEncoder.encode(str);
  const hash128 = XXH3_128(data);
  return xxh128ToBytes(hash128);
}
function nonCryptographicUuid7Deterministic(originalId, key) {
  const hashInput = `${originalId}:${key}`;
  const h = _fastHash128(hashInput);
  const b = new Uint8Array(16);
  const version = getUuidVersion(originalId);
  if (version === 7) {
    const originalBytes = uuidToBytes(originalId);
    b.set(originalBytes.slice(0, 6), 0);
  } else {
    const msecs = Date.now();
    b[0] = msecs / 1099511627776 & 255;
    b[1] = msecs / 4294967296 & 255;
    b[2] = msecs / 16777216 & 255;
    b[3] = msecs / 65536 & 255;
    b[4] = msecs / 256 & 255;
    b[5] = msecs & 255;
  }
  b[6] = 112 | h[0] & 15;
  b[7] = h[1];
  b[8] = 128 | h[2] & 63;
  b.set(h.slice(3, 10), 9);
  return bytesToUuid(b);
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/error.js
function getInvalidPromptIdentifierMsg(identifier) {
  return `Invalid prompt identifier format: "${identifier}". Expected one of:
  - "prompt-name" (for private prompts)
  - "owner/prompt-name" (for prompts with explicit owner)
  - "prompt-name:commit-hash" (with commit reference)
  - "owner/prompt-name:commit-hash" (with owner and commit)`;
}
var LangSmithConflictError = class extends Error {
  constructor(message) {
    super(message);
    Object.defineProperty(this, "status", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    this.name = "LangSmithConflictError";
    this.status = 409;
  }
};
var LangSmithNotFoundError = class extends Error {
  constructor(message) {
    super(message);
    Object.defineProperty(this, "status", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    this.name = "LangSmithNotFoundError";
    this.status = 404;
  }
};
function isLangSmithNotFoundError(error2) {
  return error2 != null && typeof error2 === "object" && "name" in error2 && error2?.name === "LangSmithNotFoundError";
}
async function raiseForStatus(response, context, consumeOnSuccess) {
  let errorBody;
  if (response.ok) {
    if (consumeOnSuccess) {
      errorBody = await response.text();
    }
    return;
  }
  if (response.status === 403) {
    try {
      const errorData = await response.json();
      const errorCode = errorData?.error;
      if (errorCode === "org_scoped_key_requires_workspace") {
        errorBody = "This API key is org-scoped and requires workspace specification. Please provide 'workspaceId' parameter, or set LANGSMITH_WORKSPACE_ID environment variable.";
      }
    } catch (e) {
      const errorWithStatus = new Error(`${response.status} ${response.statusText}`);
      errorWithStatus.status = response?.status;
      throw errorWithStatus;
    }
  }
  if (errorBody === void 0) {
    try {
      errorBody = await response.text();
    } catch (e) {
      errorBody = "";
    }
  }
  const fullMessage = `Failed to ${context}. Received status [${response.status}]: ${response.statusText}. Message: ${errorBody}`;
  if (response.status === 404) {
    throw new LangSmithNotFoundError(fullMessage);
  }
  if (response.status === 409) {
    throw new LangSmithConflictError(fullMessage);
  }
  const err = new Error(fullMessage);
  err.status = response.status;
  throw err;
}
var ERR_CONFLICTING_ENDPOINTS = "ERR_CONFLICTING_ENDPOINTS";
var ConflictingEndpointsError = class extends Error {
  constructor() {
    super("You cannot provide both LANGSMITH_ENDPOINT / LANGCHAIN_ENDPOINT and LANGSMITH_RUNS_ENDPOINTS.");
    Object.defineProperty(this, "code", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: ERR_CONFLICTING_ENDPOINTS
    });
    this.name = "ConflictingEndpointsError";
  }
};
function isConflictingEndpointsError(err) {
  return typeof err === "object" && err !== null && err.code === ERR_CONFLICTING_ENDPOINTS;
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/prompts.js
function parsePromptIdentifier(identifier) {
  if (!identifier || identifier.split("/").length > 2 || identifier.startsWith("/") || identifier.endsWith("/") || identifier.split(":").length > 2) {
    throw new Error(getInvalidPromptIdentifierMsg(identifier));
  }
  const [ownerNamePart, commitPart] = identifier.split(":");
  const commit = commitPart || "latest";
  if (ownerNamePart.includes("/")) {
    const [owner, name] = ownerNamePart.split("/", 2);
    if (!owner || !name) {
      throw new Error(getInvalidPromptIdentifierMsg(identifier));
    }
    return [owner, name, commit];
  } else {
    if (!ownerNamePart) {
      throw new Error(getInvalidPromptIdentifierMsg(identifier));
    }
    return ["-", ownerNamePart, commit];
  }
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/fs.js
import * as nodeFs from "node:fs";
import * as nodeFsPromises from "node:fs/promises";
import * as nodePath from "node:path";
var path = nodePath;
async function mkdir2(dir) {
  await nodeFsPromises.mkdir(dir, { recursive: true });
}
async function writeFileAtomic(filePath, content) {
  const tempPath = `${filePath}.tmp`;
  await nodeFsPromises.writeFile(tempPath, content, {
    encoding: "utf8",
    mode: 384
  });
  await nodeFsPromises.rename(tempPath, filePath);
}
async function readdir2(dir) {
  return nodeFsPromises.readdir(dir);
}
async function stat2(filePath) {
  return nodeFsPromises.stat(filePath);
}
function existsSync2(p) {
  return nodeFs.existsSync(p);
}
function mkdirSync2(dir) {
  nodeFs.mkdirSync(dir, { recursive: true });
}
function writeFileSync2(filePath, content) {
  nodeFs.writeFileSync(filePath, content);
}
function renameSync2(oldPath, newPath) {
  nodeFs.renameSync(oldPath, newPath);
}
function unlinkSync2(filePath) {
  nodeFs.unlinkSync(filePath);
}
function readFileSync2(filePath) {
  return nodeFs.readFileSync(filePath, "utf-8");
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/prompt_cache/index.js
function isStale(entry, ttlSeconds) {
  if (ttlSeconds === null) {
    return false;
  }
  const ageMs = Date.now() - entry.createdAt;
  return ageMs > ttlSeconds * 1e3;
}
var PromptCache = class {
  constructor(config = {}) {
    Object.defineProperty(this, "cache", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: /* @__PURE__ */ new Map()
    });
    Object.defineProperty(this, "maxSize", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "ttlSeconds", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "refreshIntervalSeconds", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "refreshTimer", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "_metrics", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: {
        hits: 0,
        misses: 0,
        refreshes: 0,
        refreshErrors: 0
      }
    });
    this.configure(config);
  }
  /**
   * Get cache performance metrics.
   */
  get metrics() {
    return { ...this._metrics };
  }
  /**
   * Get total cache requests (hits + misses).
   */
  get totalRequests() {
    return this._metrics.hits + this._metrics.misses;
  }
  /**
   * Get cache hit rate (0.0 to 1.0).
   */
  get hitRate() {
    const total = this.totalRequests;
    return total > 0 ? this._metrics.hits / total : 0;
  }
  /**
   * Reset all metrics to zero.
   */
  resetMetrics() {
    this._metrics = {
      hits: 0,
      misses: 0,
      refreshes: 0,
      refreshErrors: 0
    };
  }
  /**
   * Get a value from cache.
   *
   * Returns the cached value or undefined if not found.
   * Stale entries are still returned (background refresh handles updates).
   */
  get(key, refreshFunc) {
    if (this.maxSize === 0) {
      return void 0;
    }
    const entry = this.cache.get(key);
    if (!entry) {
      this._metrics.misses += 1;
      return void 0;
    }
    this.cache.delete(key);
    this.cache.set(key, { ...entry, refreshFunc });
    this._metrics.hits += 1;
    return entry.value;
  }
  /**
   * Set a value in the cache.
   */
  set(key, value, refreshFunc) {
    if (this.maxSize === 0) {
      return;
    }
    if (this.refreshTimer === void 0) {
      this.startRefreshLoop();
    }
    if (!this.cache.has(key) && this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey !== void 0) {
        this.cache.delete(oldestKey);
      }
    }
    const entry = {
      value,
      createdAt: Date.now(),
      refreshFunc
    };
    this.cache.delete(key);
    this.cache.set(key, entry);
  }
  /**
   * Remove a specific entry from cache.
   */
  invalidate(key) {
    this.cache.delete(key);
  }
  /**
   * Clear all cache entries.
   */
  clear() {
    this.cache.clear();
  }
  /**
   * Get the number of entries in the cache.
   */
  get size() {
    return this.cache.size;
  }
  /**
   * Stop background refresh.
   * Should be called when the client is being cleaned up.
   */
  stop() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = void 0;
    }
  }
  /**
   * Dump cache contents to a JSON file for offline use.
   */
  dump(filePath) {
    const entries = {};
    for (const [key, entry] of this.cache.entries()) {
      entries[key] = entry.value;
    }
    const dir = path.dirname(filePath);
    if (!existsSync2(dir)) {
      mkdirSync2(dir);
    }
    const tempPath = `${filePath}.tmp`;
    try {
      writeFileSync2(tempPath, JSON.stringify({ entries }, null, 2));
      renameSync2(tempPath, filePath);
    } catch (e) {
      if (existsSync2(tempPath)) {
        unlinkSync2(tempPath);
      }
      throw e;
    }
  }
  /**
   * Load cache contents from a JSON file.
   *
   * Loaded entries get a fresh TTL starting from load time.
   *
   * @returns Number of entries loaded.
   */
  load(filePath) {
    if (!existsSync2(filePath)) {
      return 0;
    }
    let entries;
    try {
      const content = readFileSync2(filePath);
      const data = JSON.parse(content);
      entries = data.entries ?? null;
    } catch {
      return 0;
    }
    if (!entries) {
      return 0;
    }
    let loaded = 0;
    const now = Date.now();
    for (const [key, value] of Object.entries(entries)) {
      if (this.cache.size >= this.maxSize) {
        break;
      }
      const entry = {
        value,
        createdAt: now
        // Fresh TTL from load time
      };
      this.cache.set(key, entry);
      loaded += 1;
    }
    return loaded;
  }
  /**
   * Start the background refresh loop.
   */
  startRefreshLoop() {
    this.stop();
    if (this.ttlSeconds !== null) {
      this.refreshTimer = setInterval(() => {
        this.refreshStaleEntries().catch((e) => {
          console.warn("Unexpected error in cache refresh loop:", e);
        });
      }, this.refreshIntervalSeconds * 1e3);
      if (this.refreshTimer.unref) {
        this.refreshTimer.unref();
      }
    }
  }
  /**
   * Get list of stale cache keys.
   */
  getStaleEntries() {
    const staleEntries = [];
    for (const [key, value] of this.cache.entries()) {
      if (isStale(value, this.ttlSeconds)) {
        staleEntries.push([key, value]);
      }
    }
    return staleEntries;
  }
  /**
   * Check for stale entries and refresh them.
   */
  async refreshStaleEntries() {
    const staleEntries = this.getStaleEntries();
    if (staleEntries.length === 0) {
      return;
    }
    for (const [key, value] of staleEntries) {
      if (value.refreshFunc !== void 0) {
        try {
          const newValue = await value.refreshFunc();
          this.set(key, newValue, value.refreshFunc);
          this._metrics.refreshes += 1;
        } catch (e) {
          this._metrics.refreshErrors += 1;
          console.warn(`Failed to refresh cache entry ${key}:`, e);
        }
      }
    }
  }
  configure(config) {
    this.stop();
    this.refreshIntervalSeconds = config.refreshIntervalSeconds ?? 60;
    this.maxSize = config.maxSize ?? 100;
    this.ttlSeconds = config.ttlSeconds ?? 5 * 60;
  }
};
var promptCacheSingleton = new PromptCache();

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/singletons/fetch.js
var DEFAULT_FETCH_IMPLEMENTATION = (...args) => fetch(...args);
var globalFetchSupportsWebStreaming = void 0;
var LANGSMITH_FETCH_IMPLEMENTATION_KEY = /* @__PURE__ */ Symbol.for("ls:fetch_implementation");
var _shouldStreamForGlobalFetchImplementation = () => {
  const overriddenFetchImpl = globalThis[LANGSMITH_FETCH_IMPLEMENTATION_KEY];
  if (overriddenFetchImpl === void 0) {
    return true;
  }
  return globalFetchSupportsWebStreaming ?? false;
};
var _getFetchImplementation = (debug2) => {
  return async (...args) => {
    if (debug2 || getLangSmithEnvironmentVariable("DEBUG") === "true") {
      const [url, options] = args;
      console.log(`\u2192 ${options?.method || "GET"} ${url}`);
    }
    const res = await (globalThis[LANGSMITH_FETCH_IMPLEMENTATION_KEY] ?? DEFAULT_FETCH_IMPLEMENTATION)(...args);
    if (debug2 || getLangSmithEnvironmentVariable("DEBUG") === "true") {
      console.log(`\u2190 ${res.status} ${res.statusText} ${res.url}`);
    }
    return res;
  };
};

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/fast-safe-stringify/index.js
var LIMIT_REPLACE_NODE = "[...]";
var CIRCULAR_REPLACE_NODE = { result: "[Circular]" };
var arr = [];
var replacerStack = [];
var encoder = new TextEncoder();
function defaultOptions() {
  return {
    depthLimit: Number.MAX_SAFE_INTEGER,
    edgesLimit: Number.MAX_SAFE_INTEGER
  };
}
function encodeString(str) {
  return encoder.encode(str);
}
function serializeWellKnownTypes(val) {
  if (val && typeof val === "object" && val !== null) {
    if (val instanceof Map) {
      return Object.fromEntries(val);
    } else if (val instanceof Set) {
      return Array.from(val);
    } else if (val instanceof Date) {
      return val.toISOString();
    } else if (val instanceof RegExp) {
      return val.toString();
    } else if (val instanceof Error) {
      return {
        name: val.name,
        message: val.message
      };
    }
  } else if (typeof val === "bigint") {
    return val.toString();
  }
  return val;
}
function createDefaultReplacer(userReplacer) {
  return function(key, val) {
    if (userReplacer) {
      const userResult = userReplacer.call(this, key, val);
      if (userResult !== void 0) {
        return userResult;
      }
    }
    return serializeWellKnownTypes(val);
  };
}
function serialize(obj, errorContext, replacer, spacer, options) {
  try {
    const str = JSON.stringify(obj, createDefaultReplacer(replacer), spacer);
    return encodeString(str);
  } catch (e) {
    if (!e.message?.includes("Converting circular structure to JSON")) {
      console.warn(`[WARNING]: LangSmith received unserializable value.${errorContext ? `
Context: ${errorContext}` : ""}`);
      return encodeString("[Unserializable]");
    }
    getLangSmithEnvironmentVariable("SUPPRESS_CIRCULAR_JSON_WARNINGS") !== "true" && console.warn(`[WARNING]: LangSmith received circular JSON. This will decrease tracer performance. ${errorContext ? `
Context: ${errorContext}` : ""}`);
    if (typeof options === "undefined") {
      options = defaultOptions();
    }
    decirc(obj, "", 0, [], void 0, 0, options);
    let res;
    try {
      if (replacerStack.length === 0) {
        res = JSON.stringify(obj, replacer, spacer);
      } else {
        res = JSON.stringify(obj, replaceGetterValues(replacer), spacer);
      }
    } catch (_) {
      return encodeString("[unable to serialize, circular reference is too complex to analyze]");
    } finally {
      while (arr.length !== 0) {
        const part = arr.pop();
        if (part.length === 4) {
          Object.defineProperty(part[0], part[1], part[3]);
        } else {
          part[0][part[1]] = part[2];
        }
      }
    }
    return encodeString(res);
  }
}
function setReplace(replace, val, k, parent) {
  var propertyDescriptor = Object.getOwnPropertyDescriptor(parent, k);
  if (propertyDescriptor.get !== void 0) {
    if (propertyDescriptor.configurable) {
      Object.defineProperty(parent, k, { value: replace });
      arr.push([parent, k, val, propertyDescriptor]);
    } else {
      replacerStack.push([val, k, replace]);
    }
  } else {
    parent[k] = replace;
    arr.push([parent, k, val]);
  }
}
function decirc(val, k, edgeIndex, stack, parent, depth, options) {
  depth += 1;
  var i;
  if (typeof val === "object" && val !== null) {
    for (i = 0; i < stack.length; i++) {
      if (stack[i] === val) {
        setReplace(CIRCULAR_REPLACE_NODE, val, k, parent);
        return;
      }
    }
    if (typeof options.depthLimit !== "undefined" && depth > options.depthLimit) {
      setReplace(LIMIT_REPLACE_NODE, val, k, parent);
      return;
    }
    if (typeof options.edgesLimit !== "undefined" && edgeIndex + 1 > options.edgesLimit) {
      setReplace(LIMIT_REPLACE_NODE, val, k, parent);
      return;
    }
    stack.push(val);
    if (Array.isArray(val)) {
      for (i = 0; i < val.length; i++) {
        decirc(val[i], i, i, stack, val, depth, options);
      }
    } else {
      val = serializeWellKnownTypes(val);
      var keys = Object.keys(val);
      for (i = 0; i < keys.length; i++) {
        var key = keys[i];
        decirc(val[key], key, i, stack, val, depth, options);
      }
    }
    stack.pop();
  }
}
function replaceGetterValues(replacer) {
  replacer = typeof replacer !== "undefined" ? replacer : function(k, v) {
    return v;
  };
  return function(key, val) {
    if (replacerStack.length > 0) {
      for (var i = 0; i < replacerStack.length; i++) {
        var part = replacerStack[i];
        if (part[1] === key && part[0] === val) {
          val = part[2];
          replacerStack.splice(i, 1);
          break;
        }
      }
    }
    return replacer.call(this, key, val);
  };
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/client.js
function _ensureUTCTimestamp(ts) {
  if (typeof ts === "string" && ts.length > 0 && !ts.includes("Z") && !ts.includes("+") && !ts.includes("-", 10)) {
    return ts + "Z";
  }
  return ts;
}
function _normalizeRunTimestamps(run) {
  return {
    ...run,
    start_time: _ensureUTCTimestamp(run.start_time),
    end_time: _ensureUTCTimestamp(run.end_time)
  };
}
function mergeRuntimeEnvIntoRun(run, cachedEnvVars, omitTracedRuntimeInfo) {
  if (omitTracedRuntimeInfo) {
    return run;
  }
  const runtimeEnv = getRuntimeEnvironment();
  const envVars = cachedEnvVars ?? getLangSmithEnvVarsMetadata();
  const extra = run.extra ?? {};
  const metadata = extra.metadata;
  run.extra = {
    ...extra,
    runtime: {
      ...runtimeEnv,
      ...extra?.runtime
    },
    metadata: {
      ...envVars,
      ...envVars.revision_id || "revision_id" in run && run.revision_id ? {
        revision_id: ("revision_id" in run ? run.revision_id : void 0) ?? envVars.revision_id
      } : {},
      ...metadata
    }
  };
  return run;
}
var getTracingSamplingRate = (configRate) => {
  const samplingRateStr = configRate?.toString() ?? getLangSmithEnvironmentVariable("TRACING_SAMPLING_RATE");
  if (samplingRateStr === void 0) {
    return void 0;
  }
  const samplingRate = parseFloat(samplingRateStr);
  if (samplingRate < 0 || samplingRate > 1) {
    throw new Error(`LANGSMITH_TRACING_SAMPLING_RATE must be between 0 and 1 if set. Got: ${samplingRate}`);
  }
  return samplingRate;
};
var isLocalhost = (url) => {
  const strippedUrl = url.replace("http://", "").replace("https://", "");
  const hostname = strippedUrl.split("/")[0].split(":")[0];
  return hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1";
};
async function toArray(iterable) {
  const result = [];
  for await (const item of iterable) {
    result.push(item);
  }
  return result;
}
function trimQuotes(str) {
  if (str === void 0) {
    return void 0;
  }
  return str.trim().replace(/^"(.*)"$/, "$1").replace(/^'(.*)'$/, "$1");
}
var handle429 = async (response) => {
  if (response?.status === 429) {
    const retryAfter = parseInt(response.headers.get("retry-after") ?? "10", 10) * 1e3;
    if (retryAfter > 0) {
      await new Promise((resolve) => setTimeout(resolve, retryAfter));
      return true;
    }
  }
  return false;
};
function _formatFeedbackScore(score) {
  if (typeof score === "number") {
    return Number(score.toFixed(4));
  }
  return score;
}
var DEFAULT_UNCOMPRESSED_BATCH_SIZE_LIMIT_BYTES = 24 * 1024 * 1024;
var DEFAULT_MAX_SIZE_BYTES = 1024 * 1024 * 1024;
var SERVER_INFO_REQUEST_TIMEOUT_MS = 1e4;
var DEFAULT_BATCH_SIZE_LIMIT = 100;
var DEFAULT_API_URL = "https://api.smith.langchain.com";
var AutoBatchQueue = class {
  constructor(maxSizeBytes) {
    Object.defineProperty(this, "items", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: []
    });
    Object.defineProperty(this, "sizeBytes", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: 0
    });
    Object.defineProperty(this, "maxSizeBytes", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    this.maxSizeBytes = maxSizeBytes ?? DEFAULT_MAX_SIZE_BYTES;
  }
  peek() {
    return this.items[0];
  }
  push(item) {
    let itemPromiseResolve;
    const itemPromise = new Promise((resolve) => {
      itemPromiseResolve = resolve;
    });
    const size = serialize(item.item, `Serializing run with id: ${item.item.id}`).length;
    if (this.sizeBytes + size > this.maxSizeBytes && this.items.length > 0) {
      console.warn(`AutoBatchQueue size limit (${this.maxSizeBytes} bytes) exceeded. Dropping run with id: ${item.item.id}. Current queue size: ${this.sizeBytes} bytes, attempted addition: ${size} bytes.`);
      itemPromiseResolve();
      return itemPromise;
    }
    this.items.push({
      action: item.action,
      payload: item.item,
      otelContext: item.otelContext,
      apiKey: item.apiKey,
      apiUrl: item.apiUrl,
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      itemPromiseResolve,
      itemPromise,
      size
    });
    this.sizeBytes += size;
    return itemPromise;
  }
  pop({ upToSizeBytes, upToSize }) {
    if (upToSizeBytes < 1) {
      throw new Error("Number of bytes to pop off may not be less than 1.");
    }
    const popped = [];
    let poppedSizeBytes = 0;
    while (poppedSizeBytes + (this.peek()?.size ?? 0) < upToSizeBytes && this.items.length > 0 && popped.length < upToSize) {
      const item = this.items.shift();
      if (item) {
        popped.push(item);
        poppedSizeBytes += item.size;
        this.sizeBytes -= item.size;
      }
    }
    if (popped.length === 0 && this.items.length > 0) {
      const item = this.items.shift();
      popped.push(item);
      poppedSizeBytes += item.size;
      this.sizeBytes -= item.size;
    }
    return [
      popped.map((it) => ({
        action: it.action,
        item: it.payload,
        otelContext: it.otelContext,
        apiKey: it.apiKey,
        apiUrl: it.apiUrl,
        size: it.size
      })),
      () => popped.forEach((it) => it.itemPromiseResolve())
    ];
  }
};
var Client = class _Client {
  get _fetch() {
    return this.fetchImplementation || _getFetchImplementation(this.debug);
  }
  constructor(config = {}) {
    Object.defineProperty(this, "apiKey", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "apiUrl", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "webUrl", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "workspaceId", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "caller", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "batchIngestCaller", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "timeout_ms", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "_tenantId", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: null
    });
    Object.defineProperty(this, "hideInputs", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "hideOutputs", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "omitTracedRuntimeInfo", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "tracingSampleRate", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "filteredPostUuids", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: /* @__PURE__ */ new Set()
    });
    Object.defineProperty(this, "autoBatchTracing", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: true
    });
    Object.defineProperty(this, "autoBatchQueue", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "autoBatchTimeout", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "autoBatchAggregationDelayMs", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: 250
    });
    Object.defineProperty(this, "batchSizeBytesLimit", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "batchSizeLimit", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "fetchOptions", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "settings", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "blockOnRootRunFinalization", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: getEnvironmentVariable("LANGSMITH_TRACING_BACKGROUND") === "false"
    });
    Object.defineProperty(this, "traceBatchConcurrency", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: 5
    });
    Object.defineProperty(this, "_serverInfo", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "_getServerInfoPromise", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "manualFlushMode", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: false
    });
    Object.defineProperty(this, "langSmithToOTELTranslator", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "fetchImplementation", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "cachedLSEnvVarsForMetadata", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "_promptCache", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "multipartStreamingDisabled", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: false
    });
    Object.defineProperty(this, "_multipartDisabled", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: false
    });
    Object.defineProperty(this, "_runCompressionDisabled", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: getLangSmithEnvironmentVariable("DISABLE_RUN_COMPRESSION") === "true"
    });
    Object.defineProperty(this, "failedTracesDir", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "failedTracesMaxBytes", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: 100 * 1024 * 1024
    });
    Object.defineProperty(this, "_customHeaders", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: {}
    });
    Object.defineProperty(this, "debug", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: getEnvironmentVariable("LANGSMITH_DEBUG") === "true"
    });
    const defaultConfig = _Client.getDefaultClientConfig();
    this.tracingSampleRate = getTracingSamplingRate(config.tracingSamplingRate);
    this.apiUrl = trimQuotes(config.apiUrl ?? defaultConfig.apiUrl) ?? "";
    if (this.apiUrl.endsWith("/")) {
      this.apiUrl = this.apiUrl.slice(0, -1);
    }
    this.apiKey = trimQuotes(config.apiKey ?? defaultConfig.apiKey);
    this.webUrl = trimQuotes(config.webUrl ?? defaultConfig.webUrl);
    if (this.webUrl?.endsWith("/")) {
      this.webUrl = this.webUrl.slice(0, -1);
    }
    this.workspaceId = trimQuotes(config.workspaceId ?? getLangSmithEnvironmentVariable("WORKSPACE_ID"));
    this.timeout_ms = config.timeout_ms ?? 9e4;
    this.caller = new AsyncCaller({
      ...config.callerOptions ?? {},
      maxRetries: 4,
      debug: config.debug ?? this.debug
    });
    this.traceBatchConcurrency = config.traceBatchConcurrency ?? this.traceBatchConcurrency;
    if (this.traceBatchConcurrency < 1) {
      throw new Error("Trace batch concurrency must be positive.");
    }
    this.debug = config.debug ?? this.debug;
    this.fetchImplementation = config.fetchImplementation;
    this.failedTracesDir = getLangSmithEnvironmentVariable("FAILED_TRACES_DIR") || void 0;
    const failedTracesMb = getLangSmithEnvironmentVariable("FAILED_TRACES_MAX_MB");
    if (failedTracesMb) {
      const n2 = parseInt(failedTracesMb, 10);
      if (Number.isFinite(n2) && n2 > 0) {
        this.failedTracesMaxBytes = n2 * 1024 * 1024;
      }
    }
    const maxMemory = config.maxIngestMemoryBytes ?? DEFAULT_MAX_SIZE_BYTES;
    this.batchIngestCaller = new AsyncCaller({
      maxRetries: 4,
      maxConcurrency: this.traceBatchConcurrency,
      maxQueueSizeBytes: maxMemory,
      ...config.callerOptions ?? {},
      onFailedResponseHook: handle429,
      debug: config.debug ?? this.debug
    });
    this.hideInputs = config.hideInputs ?? config.anonymizer ?? defaultConfig.hideInputs;
    this.hideOutputs = config.hideOutputs ?? config.anonymizer ?? defaultConfig.hideOutputs;
    this.omitTracedRuntimeInfo = config.omitTracedRuntimeInfo ?? false;
    this.autoBatchTracing = config.autoBatchTracing ?? this.autoBatchTracing;
    this.autoBatchQueue = new AutoBatchQueue(maxMemory);
    this.blockOnRootRunFinalization = config.blockOnRootRunFinalization ?? this.blockOnRootRunFinalization;
    this.batchSizeBytesLimit = config.batchSizeBytesLimit;
    this.batchSizeLimit = config.batchSizeLimit;
    this.fetchOptions = config.fetchOptions || {};
    this.manualFlushMode = config.manualFlushMode ?? this.manualFlushMode;
    if (getOtelEnabled()) {
      this.langSmithToOTELTranslator = new LangSmithToOTELTranslator();
    }
    this.cachedLSEnvVarsForMetadata = getLangSmithEnvVarsMetadata();
    if (config.cache !== void 0 && config.disablePromptCache) {
      warnOnce("Both 'cache' and 'disablePromptCache' were provided. The 'cache' parameter is deprecated and will be removed in a future version. Using 'cache' parameter value.");
    }
    if (config.cache !== void 0) {
      warnOnce("The 'cache' parameter is deprecated and will be removed in a future version. Use 'configureGlobalPromptCache()' to configure the global cache, or 'disablePromptCache: true' to disable caching for this client.");
      if (config.cache === false) {
        this._promptCache = void 0;
      } else if (config.cache === true) {
        this._promptCache = promptCacheSingleton;
      } else {
        this._promptCache = config.cache;
      }
    } else if (!config.disablePromptCache) {
      this._promptCache = promptCacheSingleton;
    }
    this._customHeaders = config.headers ?? {};
  }
  static getDefaultClientConfig() {
    const apiKey = getLangSmithEnvironmentVariable("API_KEY");
    const apiUrl = getLangSmithEnvironmentVariable("ENDPOINT") ?? DEFAULT_API_URL;
    const hideInputs = getLangSmithEnvironmentVariable("HIDE_INPUTS") === "true";
    const hideOutputs = getLangSmithEnvironmentVariable("HIDE_OUTPUTS") === "true";
    return {
      apiUrl,
      apiKey,
      webUrl: void 0,
      hideInputs,
      hideOutputs
    };
  }
  getHostUrl() {
    if (this.webUrl) {
      return this.webUrl;
    } else if (isLocalhost(this.apiUrl)) {
      this.webUrl = "http://localhost:3000";
      return this.webUrl;
    } else if (this.apiUrl.endsWith("/api/v1")) {
      this.webUrl = this.apiUrl.replace("/api/v1", "");
      return this.webUrl;
    } else if (this.apiUrl.includes("/api") && !this.apiUrl.split(".", 1)[0].endsWith("api")) {
      this.webUrl = this.apiUrl.replace("/api", "");
      return this.webUrl;
    } else if (this.apiUrl.split(".", 1)[0].includes("dev")) {
      this.webUrl = "https://dev.smith.langchain.com";
      return this.webUrl;
    } else if (this.apiUrl.split(".", 1)[0].includes("eu")) {
      this.webUrl = "https://eu.smith.langchain.com";
      return this.webUrl;
    } else if (this.apiUrl.split(".", 1)[0].includes("aws")) {
      this.webUrl = "https://aws.smith.langchain.com";
      return this.webUrl;
    } else if (this.apiUrl.split(".", 1)[0].includes("beta")) {
      this.webUrl = "https://beta.smith.langchain.com";
      return this.webUrl;
    } else {
      this.webUrl = "https://smith.langchain.com";
      return this.webUrl;
    }
  }
  get _mergedHeaders() {
    const headers = {
      "User-Agent": `langsmith-js/${__version__}`,
      ...this._customHeaders
    };
    if (this.apiKey) {
      headers["x-api-key"] = `${this.apiKey}`;
    }
    if (this.workspaceId) {
      headers["x-tenant-id"] = this.workspaceId;
    }
    return headers;
  }
  /**
   * Get or set custom headers for the client.
   * Custom headers are merged with default headers (User-Agent, x-api-key, x-tenant-id).
   * Custom headers will not override the default required headers.
   */
  get headers() {
    return this._customHeaders;
  }
  set headers(value) {
    this._customHeaders = value ?? {};
  }
  _getPlatformEndpointPath(path2) {
    const needsV1Prefix = this.apiUrl.slice(-3) !== "/v1" && this.apiUrl.slice(-4) !== "/v1/";
    return needsV1Prefix ? `/v1/platform/${path2}` : `/platform/${path2}`;
  }
  async processInputs(inputs) {
    if (this.hideInputs === false) {
      return inputs;
    }
    if (this.hideInputs === true) {
      return {};
    }
    if (typeof this.hideInputs === "function") {
      return this.hideInputs(inputs);
    }
    return inputs;
  }
  async processOutputs(outputs) {
    if (this.hideOutputs === false) {
      return outputs;
    }
    if (this.hideOutputs === true) {
      return {};
    }
    if (typeof this.hideOutputs === "function") {
      return this.hideOutputs(outputs);
    }
    return outputs;
  }
  async prepareRunCreateOrUpdateInputs(run) {
    const runParams = { ...run };
    if (runParams.inputs !== void 0) {
      runParams.inputs = await this.processInputs(runParams.inputs);
    }
    if (runParams.outputs !== void 0) {
      runParams.outputs = await this.processOutputs(runParams.outputs);
    }
    return runParams;
  }
  async _getResponse(path2, queryParams) {
    const paramsString = queryParams?.toString() ?? "";
    const url = `${this.apiUrl}${path2}?${paramsString}`;
    const response = await this.caller.call(async () => {
      const res = await this._fetch(url, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, `fetch ${path2}`);
      return res;
    });
    return response;
  }
  async _get(path2, queryParams) {
    const response = await this._getResponse(path2, queryParams);
    return response.json();
  }
  async *_getPaginated(path2, queryParams = new URLSearchParams(), transform) {
    let offset = Number(queryParams.get("offset")) || 0;
    const limit = Number(queryParams.get("limit")) || 100;
    while (true) {
      queryParams.set("offset", String(offset));
      queryParams.set("limit", String(limit));
      const url = `${this.apiUrl}${path2}?${queryParams}`;
      const response = await this.caller.call(async () => {
        const res = await this._fetch(url, {
          method: "GET",
          headers: this._mergedHeaders,
          signal: AbortSignal.timeout(this.timeout_ms),
          ...this.fetchOptions
        });
        await raiseForStatus(res, `fetch ${path2}`);
        return res;
      });
      const items = transform ? transform(await response.json()) : await response.json();
      if (items.length === 0) {
        break;
      }
      yield items;
      if (items.length < limit) {
        break;
      }
      offset += items.length;
    }
  }
  async *_getCursorPaginatedList(path2, body = null, requestMethod = "POST", dataKey = "runs") {
    const bodyParams = body ? { ...body } : {};
    while (true) {
      const body2 = JSON.stringify(bodyParams);
      const response = await this.caller.call(async () => {
        const res = await this._fetch(`${this.apiUrl}${path2}`, {
          method: requestMethod,
          headers: {
            ...this._mergedHeaders,
            "Content-Type": "application/json"
          },
          signal: AbortSignal.timeout(this.timeout_ms),
          ...this.fetchOptions,
          body: body2
        });
        await raiseForStatus(res, `fetch ${path2}`);
        return res;
      });
      const responseBody = await response.json();
      if (!responseBody) {
        break;
      }
      if (!responseBody[dataKey]) {
        break;
      }
      yield responseBody[dataKey];
      const cursors = responseBody.cursors;
      if (!cursors) {
        break;
      }
      if (!cursors.next) {
        break;
      }
      bodyParams.cursor = cursors.next;
    }
  }
  // Allows mocking for tests
  _shouldSample() {
    if (this.tracingSampleRate === void 0) {
      return true;
    }
    return Math.random() < this.tracingSampleRate;
  }
  _filterForSampling(runs, patch = false) {
    if (this.tracingSampleRate === void 0) {
      return runs;
    }
    if (patch) {
      const sampled = [];
      for (const run of runs) {
        if (!this.filteredPostUuids.has(run.trace_id)) {
          sampled.push(run);
        } else if (run.id === run.trace_id) {
          this.filteredPostUuids.delete(run.trace_id);
        }
      }
      return sampled;
    } else {
      const sampled = [];
      for (const run of runs) {
        const traceId = run.trace_id ?? run.id;
        if (this.filteredPostUuids.has(traceId)) {
          continue;
        }
        if (run.id === traceId) {
          if (this._shouldSample()) {
            sampled.push(run);
          } else {
            this.filteredPostUuids.add(traceId);
          }
        } else {
          sampled.push(run);
        }
      }
      return sampled;
    }
  }
  async _getBatchSizeLimitBytes() {
    const serverInfo = await this._ensureServerInfo();
    return this.batchSizeBytesLimit ?? serverInfo?.batch_ingest_config?.size_limit_bytes ?? DEFAULT_UNCOMPRESSED_BATCH_SIZE_LIMIT_BYTES;
  }
  /**
   * Get the maximum number of operations to batch in a single request.
   */
  async _getBatchSizeLimit() {
    const serverInfo = await this._ensureServerInfo();
    return this.batchSizeLimit ?? serverInfo?.batch_ingest_config?.size_limit ?? DEFAULT_BATCH_SIZE_LIMIT;
  }
  async _getDatasetExamplesMultiPartSupport() {
    const serverInfo = await this._ensureServerInfo();
    return serverInfo.instance_flags?.dataset_examples_multipart_enabled ?? false;
  }
  drainAutoBatchQueue({ batchSizeLimitBytes, batchSizeLimit }) {
    const promises = [];
    while (this.autoBatchQueue.items.length > 0) {
      const [batch, done] = this.autoBatchQueue.pop({
        upToSizeBytes: batchSizeLimitBytes,
        upToSize: batchSizeLimit
      });
      if (!batch.length) {
        done();
        break;
      }
      const batchesByDestination = batch.reduce((acc, item) => {
        const apiUrl = item.apiUrl ?? this.apiUrl;
        const apiKey = item.apiKey ?? this.apiKey;
        const isDefault = item.apiKey === this.apiKey && item.apiUrl === this.apiUrl;
        const batchKey = isDefault ? "default" : `${apiUrl}|${apiKey}`;
        if (!acc[batchKey]) {
          acc[batchKey] = [];
        }
        acc[batchKey].push(item);
        return acc;
      }, {});
      const batchPromises = [];
      for (const [batchKey, batch2] of Object.entries(batchesByDestination)) {
        const batchPromise = this._processBatch(batch2, {
          apiUrl: batchKey === "default" ? void 0 : batchKey.split("|")[0],
          apiKey: batchKey === "default" ? void 0 : batchKey.split("|")[1]
        });
        batchPromises.push(batchPromise);
      }
      const allBatchesPromise = Promise.all(batchPromises).finally(done);
      promises.push(allBatchesPromise);
    }
    return Promise.all(promises);
  }
  /**
   * Persist a failed trace payload to a local fallback directory.
   *
   * Saves a self-contained JSON file containing the endpoint path, the HTTP
   * headers required for replay, and the base64-encoded request body.
   * Can be replayed later with a simple POST:
   *
   *   POST /<endpoint>
   *   Content-Type: <value from saved headers>
   *   [Content-Encoding: <value from saved headers>]
   *   <decoded body>
   */
  static async _writeTraceToFallbackDir(directory, body, replayHeaders, endpoint, maxBytes) {
    try {
      const bodyBuffer = typeof body === "string" ? Buffer.from(body, "utf8") : Buffer.from(body);
      const envelope = JSON.stringify({
        version: 1,
        endpoint,
        headers: replayHeaders,
        body_base64: bodyBuffer.toString("base64")
      });
      const filename = `trace_${Date.now()}_${v4_default().slice(0, 8)}.json`;
      const filepath = path.join(directory, filename);
      if (!_Client._fallbackDirsCreated.has(directory)) {
        await mkdir2(directory);
        _Client._fallbackDirsCreated.add(directory);
      }
      if (maxBytes !== void 0 && maxBytes > 0) {
        try {
          const entries = await readdir2(directory);
          const traceFiles = entries.filter((f) => f.startsWith("trace_") && f.endsWith(".json"));
          let total = 0;
          for (const name of traceFiles) {
            const { size } = await stat2(path.join(directory, name));
            total += size;
          }
          if (total >= maxBytes) {
            console.warn(`Could not write trace to fallback dir ${directory} as it's already over size limit (${total} bytes >= ${maxBytes} bytes). Increase LANGSMITH_FAILED_TRACES_MAX_MB if possible.`);
            return;
          }
        } catch {
        }
      }
      await writeFileAtomic(filepath, envelope);
      console.warn(`LangSmith trace upload failed; data saved to ${filepath} for later replay.`);
    } catch (writeErr) {
      console.error(`LangSmith tracing error: could not write trace to fallback dir ${directory}:`, writeErr);
    }
  }
  async _processBatch(batch, options) {
    if (!batch.length) {
      return;
    }
    const batchSizeBytes = batch.reduce((sum, item) => sum + (item.size ?? 0), 0);
    try {
      if (this.langSmithToOTELTranslator !== void 0) {
        this._sendBatchToOTELTranslator(batch);
      } else {
        const ingestParams = {
          runCreates: batch.filter((item) => item.action === "create").map((item) => item.item),
          runUpdates: batch.filter((item) => item.action === "update").map((item) => item.item)
        };
        const serverInfo = await this._ensureServerInfo();
        const useMultipart = !this._multipartDisabled && (serverInfo?.batch_ingest_config?.use_multipart_endpoint ?? true);
        if (useMultipart) {
          const useGzip = !this._runCompressionDisabled && serverInfo?.instance_flags?.gzip_body_enabled;
          try {
            await this.multipartIngestRuns(ingestParams, {
              ...options,
              useGzip,
              sizeBytes: batchSizeBytes
            });
          } catch (e) {
            if (isLangSmithNotFoundError(e)) {
              this._multipartDisabled = true;
              await this.batchIngestRuns(ingestParams, {
                ...options,
                sizeBytes: batchSizeBytes
              });
            } else {
              throw e;
            }
          }
        } else {
          await this.batchIngestRuns(ingestParams, {
            ...options,
            sizeBytes: batchSizeBytes
          });
        }
      }
    } catch (e) {
      console.error("Error exporting batch:", e);
    }
  }
  _sendBatchToOTELTranslator(batch) {
    if (this.langSmithToOTELTranslator !== void 0) {
      const otelContextMap = /* @__PURE__ */ new Map();
      const operations = [];
      for (const item of batch) {
        if (item.item.id && item.otelContext) {
          otelContextMap.set(item.item.id, item.otelContext);
          if (item.action === "create") {
            operations.push({
              operation: "post",
              id: item.item.id,
              trace_id: item.item.trace_id ?? item.item.id,
              run: item.item
            });
          } else {
            operations.push({
              operation: "patch",
              id: item.item.id,
              trace_id: item.item.trace_id ?? item.item.id,
              run: item.item
            });
          }
        }
      }
      this.langSmithToOTELTranslator.exportBatch(operations, otelContextMap);
    }
  }
  async processRunOperation(item) {
    clearTimeout(this.autoBatchTimeout);
    this.autoBatchTimeout = void 0;
    item.item = mergeRuntimeEnvIntoRun(item.item, this.cachedLSEnvVarsForMetadata, this.omitTracedRuntimeInfo);
    const itemPromise = this.autoBatchQueue.push(item);
    if (this.manualFlushMode) {
      return itemPromise;
    }
    const sizeLimitBytes = await this._getBatchSizeLimitBytes();
    const sizeLimit = await this._getBatchSizeLimit();
    if (this.autoBatchQueue.sizeBytes > sizeLimitBytes || this.autoBatchQueue.items.length > sizeLimit) {
      void this.drainAutoBatchQueue({
        batchSizeLimitBytes: sizeLimitBytes,
        batchSizeLimit: sizeLimit
      });
    }
    if (this.autoBatchQueue.items.length > 0) {
      this.autoBatchTimeout = setTimeout(() => {
        this.autoBatchTimeout = void 0;
        void this.drainAutoBatchQueue({
          batchSizeLimitBytes: sizeLimitBytes,
          batchSizeLimit: sizeLimit
        });
      }, this.autoBatchAggregationDelayMs);
    }
    return itemPromise;
  }
  async _getServerInfo() {
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/info`, {
        method: "GET",
        headers: { Accept: "application/json" },
        signal: AbortSignal.timeout(SERVER_INFO_REQUEST_TIMEOUT_MS),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "get server info");
      return res;
    });
    const json = await response.json();
    if (this.debug) {
      console.log("\n=== LangSmith Server Configuration ===\n" + JSON.stringify(json, null, 2) + "\n");
    }
    return json;
  }
  async _ensureServerInfo() {
    if (this._getServerInfoPromise === void 0) {
      this._getServerInfoPromise = (async () => {
        if (this._serverInfo === void 0) {
          try {
            this._serverInfo = await this._getServerInfo();
          } catch (e) {
            console.warn(`[LANGSMITH]: Failed to fetch info on supported operations. Falling back to batch operations and default limits. Info: ${e.status ?? "Unspecified status code"} ${e.message}`);
          }
        }
        return this._serverInfo ?? {};
      })();
    }
    return this._getServerInfoPromise.then((serverInfo) => {
      if (this._serverInfo === void 0) {
        this._getServerInfoPromise = void 0;
      }
      return serverInfo;
    });
  }
  async _getSettings() {
    if (!this.settings) {
      this.settings = this._get("/settings");
    }
    return await this.settings;
  }
  /**
   * Flushes current queued traces.
   */
  async flush() {
    const sizeLimitBytes = await this._getBatchSizeLimitBytes();
    const sizeLimit = await this._getBatchSizeLimit();
    await this.drainAutoBatchQueue({
      batchSizeLimitBytes: sizeLimitBytes,
      batchSizeLimit: sizeLimit
    });
  }
  _cloneCurrentOTELContext() {
    const otel_trace = getOTELTrace();
    const otel_context = getOTELContext();
    if (this.langSmithToOTELTranslator !== void 0) {
      const currentSpan = otel_trace.getActiveSpan();
      if (currentSpan) {
        return otel_trace.setSpan(otel_context.active(), currentSpan);
      }
    }
    return void 0;
  }
  async createRun(run, options) {
    if (!this._filterForSampling([run]).length) {
      return;
    }
    const headers = {
      ...this._mergedHeaders,
      "Content-Type": "application/json"
    };
    const session_name = run.project_name;
    delete run.project_name;
    const runCreate = await this.prepareRunCreateOrUpdateInputs({
      session_name,
      ...run,
      start_time: run.start_time ?? Date.now()
    });
    if (this.autoBatchTracing && runCreate.trace_id !== void 0 && runCreate.dotted_order !== void 0) {
      const otelContext = this._cloneCurrentOTELContext();
      void this.processRunOperation({
        action: "create",
        item: runCreate,
        otelContext,
        apiKey: options?.apiKey,
        apiUrl: options?.apiUrl
      }).catch(console.error);
      return;
    }
    const mergedRunCreateParam = mergeRuntimeEnvIntoRun(runCreate, this.cachedLSEnvVarsForMetadata, this.omitTracedRuntimeInfo);
    if (options?.apiKey !== void 0) {
      headers["x-api-key"] = options.apiKey;
    }
    if (options?.workspaceId !== void 0) {
      headers["x-tenant-id"] = options.workspaceId;
    }
    const body = serialize(mergedRunCreateParam, `Creating run with id: ${mergedRunCreateParam.id}`);
    await this.caller.call(async () => {
      const res = await this._fetch(`${options?.apiUrl ?? this.apiUrl}/runs`, {
        method: "POST",
        headers,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "create run", true);
      return res;
    });
  }
  /**
   * Batch ingest/upsert multiple runs in the Langsmith system.
   * @param runs
   */
  async batchIngestRuns({ runCreates, runUpdates }, options) {
    if (runCreates === void 0 && runUpdates === void 0) {
      return;
    }
    let preparedCreateParams = await Promise.all(runCreates?.map((create) => this.prepareRunCreateOrUpdateInputs(create)) ?? []);
    let preparedUpdateParams = await Promise.all(runUpdates?.map((update) => this.prepareRunCreateOrUpdateInputs(update)) ?? []);
    if (preparedCreateParams.length > 0 && preparedUpdateParams.length > 0) {
      const createById = preparedCreateParams.reduce((params, run) => {
        if (!run.id) {
          return params;
        }
        params[run.id] = run;
        return params;
      }, {});
      const standaloneUpdates = [];
      for (const updateParam of preparedUpdateParams) {
        if (updateParam.id !== void 0 && createById[updateParam.id]) {
          createById[updateParam.id] = {
            ...createById[updateParam.id],
            ...updateParam
          };
        } else {
          standaloneUpdates.push(updateParam);
        }
      }
      preparedCreateParams = Object.values(createById);
      preparedUpdateParams = standaloneUpdates;
    }
    const rawBatch = {
      post: preparedCreateParams,
      patch: preparedUpdateParams
    };
    if (!rawBatch.post.length && !rawBatch.patch.length) {
      return;
    }
    const batchChunks = {
      post: [],
      patch: []
    };
    for (const k of ["post", "patch"]) {
      const key = k;
      const batchItems = rawBatch[key].reverse();
      let batchItem = batchItems.pop();
      while (batchItem !== void 0) {
        batchChunks[key].push(batchItem);
        batchItem = batchItems.pop();
      }
    }
    if (batchChunks.post.length > 0 || batchChunks.patch.length > 0) {
      const runIds = batchChunks.post.map((item) => item.id).concat(batchChunks.patch.map((item) => item.id)).join(",");
      await this._postBatchIngestRuns(serialize(batchChunks, `Ingesting runs with ids: ${runIds}`), options);
    }
  }
  async _postBatchIngestRuns(body, options) {
    const headers = {
      ...this._mergedHeaders,
      "Content-Type": "application/json",
      Accept: "application/json"
    };
    if (options?.apiKey !== void 0) {
      headers["x-api-key"] = options.apiKey;
    }
    await this.batchIngestCaller.callWithOptions({ sizeBytes: options?.sizeBytes }, async () => {
      const res = await this._fetch(`${options?.apiUrl ?? this.apiUrl}/runs/batch`, {
        method: "POST",
        headers,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "batch create run", true);
      return res;
    });
  }
  /**
   * Batch ingest/upsert multiple runs in the Langsmith system.
   * @param runs
   */
  async multipartIngestRuns({ runCreates, runUpdates }, options) {
    if (runCreates === void 0 && runUpdates === void 0) {
      return;
    }
    const allAttachments = {};
    let preparedCreateParams = [];
    for (const create of runCreates ?? []) {
      const preparedCreate = await this.prepareRunCreateOrUpdateInputs(create);
      if (preparedCreate.id !== void 0 && preparedCreate.attachments !== void 0) {
        allAttachments[preparedCreate.id] = preparedCreate.attachments;
      }
      delete preparedCreate.attachments;
      preparedCreateParams.push(preparedCreate);
    }
    let preparedUpdateParams = [];
    for (const update of runUpdates ?? []) {
      preparedUpdateParams.push(await this.prepareRunCreateOrUpdateInputs(update));
    }
    const invalidRunCreate = preparedCreateParams.find((runCreate) => {
      return runCreate.trace_id === void 0 || runCreate.dotted_order === void 0;
    });
    if (invalidRunCreate !== void 0) {
      throw new Error(`Multipart ingest requires "trace_id" and "dotted_order" to be set when creating a run`);
    }
    const invalidRunUpdate = preparedUpdateParams.find((runUpdate) => {
      return runUpdate.trace_id === void 0 || runUpdate.dotted_order === void 0;
    });
    if (invalidRunUpdate !== void 0) {
      throw new Error(`Multipart ingest requires "trace_id" and "dotted_order" to be set when updating a run`);
    }
    if (preparedCreateParams.length > 0 && preparedUpdateParams.length > 0) {
      const createById = preparedCreateParams.reduce((params, run) => {
        if (!run.id) {
          return params;
        }
        params[run.id] = run;
        return params;
      }, {});
      const standaloneUpdates = [];
      for (const updateParam of preparedUpdateParams) {
        if (updateParam.id !== void 0 && createById[updateParam.id]) {
          createById[updateParam.id] = {
            ...createById[updateParam.id],
            ...updateParam
          };
        } else {
          standaloneUpdates.push(updateParam);
        }
      }
      preparedCreateParams = Object.values(createById);
      preparedUpdateParams = standaloneUpdates;
    }
    if (preparedCreateParams.length === 0 && preparedUpdateParams.length === 0) {
      return;
    }
    const accumulatedContext = [];
    const accumulatedParts = [];
    for (const [method, payloads] of [
      ["post", preparedCreateParams],
      ["patch", preparedUpdateParams]
    ]) {
      for (const originalPayload of payloads) {
        const { inputs, outputs, events, extra, error: error2, serialized, attachments, ...payload } = originalPayload;
        const fields = { inputs, outputs, events, extra, error: error2, serialized };
        const stringifiedPayload = serialize(payload, `Serializing for multipart ingestion of run with id: ${payload.id}`);
        accumulatedParts.push({
          name: `${method}.${payload.id}`,
          payload: new Blob([stringifiedPayload], {
            type: `application/json; length=${stringifiedPayload.length}`
            // encoding=gzip
          })
        });
        for (const [key, value] of Object.entries(fields)) {
          if (value === void 0) {
            continue;
          }
          const stringifiedValue = serialize(value, `Serializing ${key} for multipart ingestion of run with id: ${payload.id}`);
          accumulatedParts.push({
            name: `${method}.${payload.id}.${key}`,
            payload: new Blob([stringifiedValue], {
              type: `application/json; length=${stringifiedValue.length}`
            })
          });
        }
        if (payload.id !== void 0) {
          const attachments2 = allAttachments[payload.id];
          if (attachments2) {
            delete allAttachments[payload.id];
            for (const [name, attachment] of Object.entries(attachments2)) {
              let contentType;
              let content;
              if (Array.isArray(attachment)) {
                [contentType, content] = attachment;
              } else {
                contentType = attachment.mimeType;
                content = attachment.data;
              }
              if (name.includes(".")) {
                console.warn(`Skipping attachment '${name}' for run ${payload.id}: Invalid attachment name. Attachment names must not contain periods ('.'). Please rename the attachment and try again.`);
                continue;
              }
              accumulatedParts.push({
                name: `attachment.${payload.id}.${name}`,
                payload: new Blob([content], {
                  type: `${contentType}; length=${content.byteLength}`
                })
              });
            }
          }
        }
        accumulatedContext.push(`trace=${payload.trace_id},id=${payload.id}`);
      }
    }
    await this._sendMultipartRequest(accumulatedParts, accumulatedContext.join("; "), options);
  }
  async _createNodeFetchBody(parts, boundary) {
    const chunks = [];
    for (const part of parts) {
      chunks.push(new Blob([`--${boundary}\r
`]));
      chunks.push(new Blob([
        `Content-Disposition: form-data; name="${part.name}"\r
`,
        `Content-Type: ${part.payload.type}\r
\r
`
      ]));
      chunks.push(part.payload);
      chunks.push(new Blob(["\r\n"]));
    }
    chunks.push(new Blob([`--${boundary}--\r
`]));
    const body = new Blob(chunks);
    const arrayBuffer = await body.arrayBuffer();
    return arrayBuffer;
  }
  async _createMultipartStream(parts, boundary) {
    const encoder2 = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        const writeChunk = async (chunk) => {
          if (typeof chunk === "string") {
            controller.enqueue(encoder2.encode(chunk));
          } else {
            controller.enqueue(chunk);
          }
        };
        for (const part of parts) {
          await writeChunk(`--${boundary}\r
`);
          await writeChunk(`Content-Disposition: form-data; name="${part.name}"\r
`);
          await writeChunk(`Content-Type: ${part.payload.type}\r
\r
`);
          const payloadStream = part.payload.stream();
          const reader = payloadStream.getReader();
          try {
            let result;
            while (!(result = await reader.read()).done) {
              controller.enqueue(result.value);
            }
          } finally {
            reader.releaseLock();
          }
          await writeChunk("\r\n");
        }
        await writeChunk(`--${boundary}--\r
`);
        controller.close();
      }
    });
    return stream;
  }
  async _sendMultipartRequest(parts, context, options) {
    const boundary = "----LangSmithFormBoundary" + Math.random().toString(36).slice(2);
    const buildBuffered = () => this._createNodeFetchBody(parts, boundary);
    const buildStream = () => this._createMultipartStream(parts, boundary);
    const sendWithRetry = async (bodyFactory) => {
      return this.batchIngestCaller.callWithOptions({ sizeBytes: options?.sizeBytes }, async () => {
        const body = await bodyFactory();
        const headers = {
          ...this._mergedHeaders,
          "Content-Type": `multipart/form-data; boundary=${boundary}`
        };
        if (options?.apiKey !== void 0) {
          headers["x-api-key"] = options.apiKey;
        }
        let transformedBody = body;
        if (options?.useGzip && typeof body === "object" && "pipeThrough" in body) {
          transformedBody = body.pipeThrough(new CompressionStream("gzip"));
          headers["Content-Encoding"] = "gzip";
        }
        const response = await this._fetch(`${options?.apiUrl ?? this.apiUrl}/runs/multipart`, {
          method: "POST",
          headers,
          body: transformedBody,
          duplex: "half",
          signal: AbortSignal.timeout(this.timeout_ms),
          ...this.fetchOptions
        });
        await raiseForStatus(response, `Failed to send multipart request`, true);
        return response;
      });
    };
    try {
      let res;
      let streamedAttempt = false;
      const shouldStream = _shouldStreamForGlobalFetchImplementation();
      if (shouldStream && !this.multipartStreamingDisabled && getEnv() !== "bun") {
        streamedAttempt = true;
        res = await sendWithRetry(buildStream);
      } else {
        res = await sendWithRetry(buildBuffered);
      }
      if ((!this.multipartStreamingDisabled || streamedAttempt) && res.status === 422 && (options?.apiUrl ?? this.apiUrl) !== DEFAULT_API_URL) {
        console.warn(`Streaming multipart upload to ${options?.apiUrl ?? this.apiUrl}/runs/multipart failed. This usually means the host does not support chunked uploads. Retrying with a buffered upload for operation "${context}".`);
        this.multipartStreamingDisabled = true;
        res = await sendWithRetry(buildBuffered);
      }
    } catch (e) {
      if (isLangSmithNotFoundError(e)) {
        throw e;
      }
      console.warn(`${e.message.trim()}

Context: ${context}`);
      if (this.failedTracesDir) {
        const bodyBuffer = await this._createNodeFetchBody(parts, boundary).catch(() => null);
        if (bodyBuffer) {
          await _Client._writeTraceToFallbackDir(this.failedTracesDir, bodyBuffer, { "Content-Type": `multipart/form-data; boundary=${boundary}` }, "runs/multipart", this.failedTracesMaxBytes);
        }
      }
    }
  }
  async updateRun(runId, run, options) {
    assertUuid(runId);
    if (run.inputs) {
      run.inputs = await this.processInputs(run.inputs);
    }
    if (run.outputs) {
      run.outputs = await this.processOutputs(run.outputs);
    }
    const data = { ...run, id: runId };
    if (!this._filterForSampling([data], true).length) {
      return;
    }
    if (this.autoBatchTracing && data.trace_id !== void 0 && data.dotted_order !== void 0) {
      const otelContext = this._cloneCurrentOTELContext();
      if (run.end_time !== void 0 && data.parent_run_id === void 0 && this.blockOnRootRunFinalization && !this.manualFlushMode) {
        await this.processRunOperation({
          action: "update",
          item: data,
          otelContext,
          apiKey: options?.apiKey,
          apiUrl: options?.apiUrl
        }).catch(console.error);
        return;
      } else {
        void this.processRunOperation({
          action: "update",
          item: data,
          otelContext,
          apiKey: options?.apiKey,
          apiUrl: options?.apiUrl
        }).catch(console.error);
      }
      return;
    }
    const headers = {
      ...this._mergedHeaders,
      "Content-Type": "application/json"
    };
    if (options?.apiKey !== void 0) {
      headers["x-api-key"] = options.apiKey;
    }
    if (options?.workspaceId !== void 0) {
      headers["x-tenant-id"] = options.workspaceId;
    }
    const body = serialize(run, `Serializing payload to update run with id: ${runId}`);
    await this.caller.call(async () => {
      const res = await this._fetch(`${options?.apiUrl ?? this.apiUrl}/runs/${runId}`, {
        method: "PATCH",
        headers,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "update run", true);
      return res;
    });
  }
  async readRun(runId, { loadChildRuns } = { loadChildRuns: false }) {
    assertUuid(runId);
    let run = _normalizeRunTimestamps(await this._get(`/runs/${runId}`));
    if (loadChildRuns) {
      run = await this._loadChildRuns(run);
    }
    return run;
  }
  async getRunUrl({ runId, run, projectOpts }) {
    if (run !== void 0) {
      let sessionId;
      if (run.session_id) {
        sessionId = run.session_id;
      } else if (projectOpts?.projectName) {
        sessionId = (await this.readProject({ projectName: projectOpts?.projectName })).id;
      } else if (projectOpts?.projectId) {
        sessionId = projectOpts?.projectId;
      } else {
        const project = await this.readProject({
          projectName: getLangSmithEnvironmentVariable("PROJECT") || "default"
        });
        sessionId = project.id;
      }
      const tenantId = await this._getTenantId();
      return `${this.getHostUrl()}/o/${tenantId}/projects/p/${sessionId}/r/${run.id}?poll=true`;
    } else if (runId !== void 0) {
      const run_ = await this.readRun(runId);
      if (!run_.app_path) {
        throw new Error(`Run ${runId} has no app_path`);
      }
      const baseUrl = this.getHostUrl();
      return `${baseUrl}${run_.app_path}`;
    } else {
      throw new Error("Must provide either runId or run");
    }
  }
  async _loadChildRuns(run) {
    const childRuns = await toArray(this.listRuns({
      isRoot: false,
      projectId: run.session_id,
      traceId: run.trace_id
    }));
    const treemap = {};
    const runs = {};
    childRuns.sort((a, b) => (a?.dotted_order ?? "").localeCompare(b?.dotted_order ?? ""));
    for (const childRun of childRuns) {
      if (childRun.parent_run_id === null || childRun.parent_run_id === void 0) {
        throw new Error(`Child run ${childRun.id} has no parent`);
      }
      if (childRun.dotted_order?.startsWith(run.dotted_order ?? "") && childRun.id !== run.id) {
        if (!(childRun.parent_run_id in treemap)) {
          treemap[childRun.parent_run_id] = [];
        }
        treemap[childRun.parent_run_id].push(childRun);
        runs[childRun.id] = childRun;
      }
    }
    run.child_runs = treemap[run.id] || [];
    for (const runId in treemap) {
      if (runId !== run.id) {
        runs[runId].child_runs = treemap[runId];
      }
    }
    return run;
  }
  /**
   * List runs from the LangSmith server.
   * @param projectId - The ID of the project to filter by.
   * @param projectName - The name of the project to filter by.
   * @param parentRunId - The ID of the parent run to filter by.
   * @param traceId - The ID of the trace to filter by.
   * @param referenceExampleId - The ID of the reference example to filter by.
   * @param startTime - The start time to filter by.
   * @param isRoot - Indicates whether to only return root runs.
   * @param runType - The run type to filter by.
   * @param error - Indicates whether to filter by error runs.
   * @param id - The ID of the run to filter by.
   * @param query - The query string to filter by.
   * @param filter - The filter string to apply to the run spans.
   * @param traceFilter - The filter string to apply on the root run of the trace.
   * @param treeFilter - The filter string to apply on other runs in the trace.
   * @param limit - The maximum number of runs to retrieve.
   * @returns {AsyncIterable<Run>} - The runs.
   *
   * @example
   * // List all runs in a project
   * const projectRuns = client.listRuns({ projectName: "<your_project>" });
   *
   * @example
   * // List LLM and Chat runs in the last 24 hours
   * const todaysLLMRuns = client.listRuns({
   *   projectName: "<your_project>",
   *   start_time: new Date(Date.now() - 24 * 60 * 60 * 1000),
   *   run_type: "llm",
   * });
   *
   * @example
   * // List traces in a project
   * const rootRuns = client.listRuns({
   *   projectName: "<your_project>",
   *   execution_order: 1,
   * });
   *
   * @example
   * // List runs without errors
   * const correctRuns = client.listRuns({
   *   projectName: "<your_project>",
   *   error: false,
   * });
   *
   * @example
   * // List runs by run ID
   * const runIds = [
   *   "a36092d2-4ad5-4fb4-9c0d-0dba9a2ed836",
   *   "9398e6be-964f-4aa4-8ae9-ad78cd4b7074",
   * ];
   * const selectedRuns = client.listRuns({ run_ids: runIds });
   *
   * @example
   * // List all "chain" type runs that took more than 10 seconds and had `total_tokens` greater than 5000
   * const chainRuns = client.listRuns({
   *   projectName: "<your_project>",
   *   filter: 'and(eq(run_type, "chain"), gt(latency, 10), gt(total_tokens, 5000))',
   * });
   *
   * @example
   * // List all runs called "extractor" whose root of the trace was assigned feedback "user_score" score of 1
   * const goodExtractorRuns = client.listRuns({
   *   projectName: "<your_project>",
   *   filter: 'eq(name, "extractor")',
   *   traceFilter: 'and(eq(feedback_key, "user_score"), eq(feedback_score, 1))',
   * });
   *
   * @example
   * // List all runs that started after a specific timestamp and either have "error" not equal to null or a "Correctness" feedback score equal to 0
   * const complexRuns = client.listRuns({
   *   projectName: "<your_project>",
   *   filter: 'and(gt(start_time, "2023-07-15T12:34:56Z"), or(neq(error, null), and(eq(feedback_key, "Correctness"), eq(feedback_score, 0.0))))',
   * });
   *
   * @example
   * // List all runs where `tags` include "experimental" or "beta" and `latency` is greater than 2 seconds
   * const taggedRuns = client.listRuns({
   *   projectName: "<your_project>",
   *   filter: 'and(or(has(tags, "experimental"), has(tags, "beta")), gt(latency, 2))',
   * });
   */
  async *listRuns(props) {
    const { projectId, projectName, parentRunId, traceId, referenceExampleId, startTime, executionOrder, isRoot, runType, error: error2, id, query, filter, traceFilter, treeFilter, limit, select, order } = props;
    let projectIds = [];
    if (projectId) {
      projectIds = Array.isArray(projectId) ? projectId : [projectId];
    }
    if (projectName) {
      const projectNames = Array.isArray(projectName) ? projectName : [projectName];
      const projectIds_ = await Promise.all(projectNames.map((name) => this.readProject({ projectName: name }).then((project) => project.id)));
      projectIds.push(...projectIds_);
    }
    const default_select = [
      "app_path",
      "completion_cost",
      "completion_tokens",
      "dotted_order",
      "end_time",
      "error",
      "events",
      "extra",
      "feedback_stats",
      "first_token_time",
      "id",
      "inputs",
      "name",
      "outputs",
      "parent_run_id",
      "parent_run_ids",
      "prompt_cost",
      "prompt_tokens",
      "reference_example_id",
      "run_type",
      "session_id",
      "start_time",
      "status",
      "tags",
      "total_cost",
      "total_tokens",
      "trace_id"
    ];
    const body = {
      session: projectIds.length ? projectIds : null,
      run_type: runType,
      reference_example: referenceExampleId,
      query,
      filter,
      trace_filter: traceFilter,
      tree_filter: treeFilter,
      execution_order: executionOrder,
      parent_run: parentRunId,
      start_time: startTime ? startTime.toISOString() : null,
      error: error2,
      id,
      limit,
      trace: traceId,
      select: select ? select : default_select,
      is_root: isRoot,
      order
    };
    if (body.select.includes("child_run_ids")) {
      warnOnce("Deprecated: 'child_run_ids' in the listRuns select parameter is deprecated and will be removed in a future version.");
    }
    let runsYielded = 0;
    for await (const runs of this._getCursorPaginatedList("/runs/query", body)) {
      const normalized = runs.map(_normalizeRunTimestamps);
      if (limit) {
        if (runsYielded >= limit) {
          break;
        }
        if (normalized.length + runsYielded > limit) {
          const newRuns = normalized.slice(0, limit - runsYielded);
          yield* newRuns;
          break;
        }
        runsYielded += normalized.length;
        yield* normalized;
      } else {
        yield* normalized;
      }
    }
  }
  async *listGroupRuns(props) {
    const { projectId, projectName, groupBy, filter, startTime, endTime, limit, offset } = props;
    const sessionId = projectId || (await this.readProject({ projectName })).id;
    const baseBody = {
      session_id: sessionId,
      group_by: groupBy,
      filter,
      start_time: startTime ? startTime.toISOString() : null,
      end_time: endTime ? endTime.toISOString() : null,
      limit: Number(limit) || 100
    };
    let currentOffset = Number(offset) || 0;
    const path2 = "/runs/group";
    const url = `${this.apiUrl}${path2}`;
    while (true) {
      const currentBody = {
        ...baseBody,
        offset: currentOffset
      };
      const filteredPayload = Object.fromEntries(Object.entries(currentBody).filter(([_, value]) => value !== void 0));
      const body = JSON.stringify(filteredPayload);
      const response = await this.caller.call(async () => {
        const res = await this._fetch(url, {
          method: "POST",
          headers: {
            ...this._mergedHeaders,
            "Content-Type": "application/json"
          },
          signal: AbortSignal.timeout(this.timeout_ms),
          ...this.fetchOptions,
          body
        });
        await raiseForStatus(res, `Failed to fetch ${path2}`);
        return res;
      });
      const items = await response.json();
      const { groups, total } = items;
      if (groups.length === 0) {
        break;
      }
      for (const thread of groups) {
        yield thread;
      }
      currentOffset += groups.length;
      if (currentOffset >= total) {
        break;
      }
    }
  }
  async *readThread(props) {
    const { threadId, projectId, projectName, isRoot = true, limit, filter: userFilter, order = "asc" } = props;
    if (!projectId && !projectName) {
      throw new Error("threadId requires projectId or projectName");
    }
    const threadFilter = `eq(thread_id, ${JSON.stringify(threadId)})`;
    const combinedFilter = userFilter ? `and(${threadFilter}, ${userFilter})` : threadFilter;
    yield* this.listRuns({
      projectId: projectId ?? void 0,
      projectName: projectName ?? void 0,
      isRoot,
      limit,
      filter: combinedFilter,
      order
    });
  }
  async listThreads(props) {
    const { projectId, projectName, limit, offset = 0, filter, startTime, isRoot = true } = props;
    if (!projectId && !projectName) {
      throw new Error("Either projectId or projectName must be provided");
    }
    if (projectId && projectName) {
      throw new Error("Provide exactly one of projectId or projectName");
    }
    const sessionId = projectId ?? (await this.readProject({ projectName })).id;
    const startTimeResolved = startTime ?? new Date(Date.now() - 1 * 24 * 60 * 60 * 1e3);
    const runSelect = [
      "id",
      "name",
      "status",
      "start_time",
      "end_time",
      "thread_id",
      "trace_id",
      "run_type",
      "error",
      "tags",
      "session_id",
      "parent_run_id",
      "total_tokens",
      "total_cost",
      "dotted_order",
      "reference_example_id",
      "feedback_stats",
      "app_path",
      "completion_cost",
      "completion_tokens",
      "prompt_cost",
      "prompt_tokens",
      "first_token_time"
    ];
    const bodyQuery = {
      session: [sessionId],
      is_root: isRoot,
      limit: 100,
      order: "desc",
      select: runSelect,
      start_time: startTimeResolved.toISOString()
    };
    if (filter != null) {
      bodyQuery.filter = filter;
    }
    const threadsMap = /* @__PURE__ */ new Map();
    for await (const runs of this._getCursorPaginatedList("/runs/query", bodyQuery)) {
      for (const raw of runs) {
        const run = _normalizeRunTimestamps(raw);
        const tid = run.thread_id;
        if (tid) {
          const list = threadsMap.get(tid) ?? [];
          list.push(run);
          threadsMap.set(tid, list);
        }
      }
    }
    const result = [];
    for (const [threadId, runs] of threadsMap.entries()) {
      runs.sort((a, b) => {
        const aRun = a;
        const bRun = b;
        const aStart = aRun.start_time ?? "";
        const bStart = bRun.start_time ?? "";
        if (aStart !== bStart)
          return aStart.localeCompare(bStart);
        const aOrder = aRun.dotted_order ?? "";
        const bOrder = bRun.dotted_order ?? "";
        return aOrder.localeCompare(bOrder);
      });
      const startTimes = runs.map((r) => r.start_time).filter(Boolean);
      const sortedTimes = [...startTimes].sort();
      const minStart = sortedTimes.length ? sortedTimes[0] : "";
      const maxStart = sortedTimes.length ? sortedTimes[sortedTimes.length - 1] : "";
      result.push({
        thread_id: threadId,
        runs,
        count: runs.length,
        filter: "",
        total_tokens: 0,
        total_cost: null,
        min_start_time: minStart,
        max_start_time: maxStart,
        latency_p50: 0,
        latency_p99: 0,
        feedback_stats: null,
        first_inputs: "",
        last_outputs: "",
        last_error: null
      });
    }
    result.sort((a, b) => {
      const aMax = a.max_start_time ?? "";
      const bMax = b.max_start_time ?? "";
      return bMax.localeCompare(aMax);
    });
    const withOffset = offset > 0 ? result.slice(offset) : result;
    const withLimit = limit !== void 0 ? withOffset.slice(0, limit) : withOffset;
    return withLimit;
  }
  async getRunStats({ id, trace, parentRun, runType, projectNames, projectIds, referenceExampleIds, startTime, endTime, error: error2, query, filter, traceFilter, treeFilter, isRoot, dataSourceType }) {
    let projectIds_ = projectIds || [];
    if (projectNames) {
      projectIds_ = [
        ...projectIds || [],
        ...await Promise.all(projectNames.map((name) => this.readProject({ projectName: name }).then((project) => project.id)))
      ];
    }
    const payload = {
      id,
      trace,
      parent_run: parentRun,
      run_type: runType,
      session: projectIds_,
      reference_example: referenceExampleIds,
      start_time: startTime,
      end_time: endTime,
      error: error2,
      query,
      filter,
      trace_filter: traceFilter,
      tree_filter: treeFilter,
      is_root: isRoot,
      data_source_type: dataSourceType
    };
    const filteredPayload = Object.fromEntries(Object.entries(payload).filter(([_, value]) => value !== void 0));
    const body = JSON.stringify(filteredPayload);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/runs/stats`, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "get run stats");
      return res;
    });
    const result = await response.json();
    return result;
  }
  async shareRun(runId, { shareId } = {}) {
    const data = {
      run_id: runId,
      share_token: shareId || v4_default()
    };
    assertUuid(runId);
    const body = JSON.stringify(data);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/runs/${runId}/share`, {
        method: "PUT",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "share run");
      return res;
    });
    const result = await response.json();
    if (result === null || !("share_token" in result)) {
      throw new Error("Invalid response from server");
    }
    return `${this.getHostUrl()}/public/${result["share_token"]}/r`;
  }
  async unshareRun(runId) {
    assertUuid(runId);
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/runs/${runId}/share`, {
        method: "DELETE",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "unshare run", true);
      return res;
    });
  }
  async readRunSharedLink(runId) {
    assertUuid(runId);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/runs/${runId}/share`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "read run shared link");
      return res;
    });
    const result = await response.json();
    if (result === null || !("share_token" in result)) {
      return void 0;
    }
    return `${this.getHostUrl()}/public/${result["share_token"]}/r`;
  }
  async listSharedRuns(shareToken, { runIds } = {}) {
    const queryParams = new URLSearchParams({
      share_token: shareToken
    });
    if (runIds !== void 0) {
      for (const runId of runIds) {
        queryParams.append("id", runId);
      }
    }
    assertUuid(shareToken);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/public/${shareToken}/runs${queryParams}`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "list shared runs");
      return res;
    });
    const runs = await response.json();
    return runs.map(_normalizeRunTimestamps);
  }
  async readDatasetSharedSchema(datasetId, datasetName) {
    if (!datasetId && !datasetName) {
      throw new Error("Either datasetId or datasetName must be given");
    }
    if (!datasetId) {
      const dataset = await this.readDataset({ datasetName });
      datasetId = dataset.id;
    }
    assertUuid(datasetId);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets/${datasetId}/share`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "read dataset shared schema");
      return res;
    });
    const shareSchema = await response.json();
    shareSchema.url = `${this.getHostUrl()}/public/${shareSchema.share_token}/d`;
    return shareSchema;
  }
  async shareDataset(datasetId, datasetName) {
    if (!datasetId && !datasetName) {
      throw new Error("Either datasetId or datasetName must be given");
    }
    if (!datasetId) {
      const dataset = await this.readDataset({ datasetName });
      datasetId = dataset.id;
    }
    const data = {
      dataset_id: datasetId
    };
    assertUuid(datasetId);
    const body = JSON.stringify(data);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets/${datasetId}/share`, {
        method: "PUT",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "share dataset");
      return res;
    });
    const shareSchema = await response.json();
    shareSchema.url = `${this.getHostUrl()}/public/${shareSchema.share_token}/d`;
    return shareSchema;
  }
  async unshareDataset(datasetId) {
    assertUuid(datasetId);
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets/${datasetId}/share`, {
        method: "DELETE",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "unshare dataset", true);
      return res;
    });
  }
  async readSharedDataset(shareToken) {
    assertUuid(shareToken);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/public/${shareToken}/datasets`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "read shared dataset");
      return res;
    });
    const dataset = await response.json();
    return dataset;
  }
  /**
   * Get shared examples.
   *
   * @param {string} shareToken The share token to get examples for. A share token is the UUID (or LangSmith URL, including UUID) generated when explicitly marking an example as public.
   * @param {Object} [options] Additional options for listing the examples.
   * @param {string[] | undefined} [options.exampleIds] A list of example IDs to filter by.
   * @returns {Promise<Example[]>} The shared examples.
   */
  async listSharedExamples(shareToken, options) {
    const params = {};
    if (options?.exampleIds) {
      params.id = options.exampleIds;
    }
    const urlParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach((v) => urlParams.append(key, v));
      } else {
        urlParams.append(key, value);
      }
    });
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/public/${shareToken}/examples?${urlParams.toString()}`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "list shared examples");
      return res;
    });
    const result = await response.json();
    if (!response.ok) {
      if ("detail" in result) {
        throw new Error(`Failed to list shared examples.
Status: ${response.status}
Message: ${Array.isArray(result.detail) ? result.detail.join("\n") : "Unspecified error"}`);
      }
      throw new Error(`Failed to list shared examples: ${response.status} ${response.statusText}`);
    }
    return result.map((example) => ({
      ...example,
      _hostUrl: this.getHostUrl()
    }));
  }
  async createProject({ projectName, description = null, metadata = null, upsert = false, projectExtra = null, referenceDatasetId = null }) {
    const upsert_ = upsert ? `?upsert=true` : "";
    const endpoint = `${this.apiUrl}/sessions${upsert_}`;
    const extra = projectExtra || {};
    if (metadata) {
      extra["metadata"] = metadata;
    }
    const body = {
      name: projectName,
      extra,
      description
    };
    if (referenceDatasetId !== null) {
      body["reference_dataset_id"] = referenceDatasetId;
    }
    const serializedBody = JSON.stringify(body);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(endpoint, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: serializedBody
      });
      await raiseForStatus(res, "create project");
      return res;
    });
    const result = await response.json();
    return result;
  }
  async updateProject(projectId, { name = null, description = null, metadata = null, projectExtra = null, endTime = null }) {
    const endpoint = `${this.apiUrl}/sessions/${projectId}`;
    let extra = projectExtra;
    if (metadata) {
      extra = { ...extra || {}, metadata };
    }
    const body = JSON.stringify({
      name,
      extra,
      description,
      end_time: endTime ? new Date(endTime).toISOString() : null
    });
    const response = await this.caller.call(async () => {
      const res = await this._fetch(endpoint, {
        method: "PATCH",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "update project");
      return res;
    });
    const result = await response.json();
    return result;
  }
  async hasProject({ projectId, projectName }) {
    let path2 = "/sessions";
    const params = new URLSearchParams();
    if (projectId !== void 0 && projectName !== void 0) {
      throw new Error("Must provide either projectName or projectId, not both");
    } else if (projectId !== void 0) {
      assertUuid(projectId);
      path2 += `/${projectId}`;
    } else if (projectName !== void 0) {
      params.append("name", projectName);
    } else {
      throw new Error("Must provide projectName or projectId");
    }
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}${path2}?${params}`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "has project");
      return res;
    });
    try {
      const result = await response.json();
      if (!response.ok) {
        return false;
      }
      if (Array.isArray(result)) {
        return result.length > 0;
      }
      return true;
    } catch (e) {
      return false;
    }
  }
  async readProject({ projectId, projectName, includeStats }) {
    let path2 = "/sessions";
    const params = new URLSearchParams();
    if (projectId !== void 0 && projectName !== void 0) {
      throw new Error("Must provide either projectName or projectId, not both");
    } else if (projectId !== void 0) {
      assertUuid(projectId);
      path2 += `/${projectId}`;
    } else if (projectName !== void 0) {
      params.append("name", projectName);
    } else {
      throw new Error("Must provide projectName or projectId");
    }
    if (includeStats !== void 0) {
      params.append("include_stats", includeStats.toString());
    }
    const response = await this._get(path2, params);
    let result;
    if (Array.isArray(response)) {
      if (response.length === 0) {
        throw new Error(`Project[id=${projectId}, name=${projectName}] not found`);
      }
      result = response[0];
    } else {
      result = response;
    }
    return result;
  }
  async getProjectUrl({ projectId, projectName }) {
    if (projectId === void 0 && projectName === void 0) {
      throw new Error("Must provide either projectName or projectId");
    }
    const project = await this.readProject({ projectId, projectName });
    const tenantId = await this._getTenantId();
    return `${this.getHostUrl()}/o/${tenantId}/projects/p/${project.id}`;
  }
  async getDatasetUrl({ datasetId, datasetName }) {
    if (datasetId === void 0 && datasetName === void 0) {
      throw new Error("Must provide either datasetName or datasetId");
    }
    const dataset = await this.readDataset({ datasetId, datasetName });
    const tenantId = await this._getTenantId();
    return `${this.getHostUrl()}/o/${tenantId}/datasets/${dataset.id}`;
  }
  async _getTenantId() {
    if (this._tenantId !== null) {
      return this._tenantId;
    }
    const queryParams = new URLSearchParams({ limit: "1" });
    for await (const projects of this._getPaginated("/sessions", queryParams)) {
      this._tenantId = projects[0].tenant_id;
      return projects[0].tenant_id;
    }
    throw new Error("No projects found to resolve tenant.");
  }
  async *listProjects({ projectIds, name, nameContains, referenceDatasetId, referenceDatasetName, includeStats, datasetVersion, referenceFree, metadata } = {}) {
    const params = new URLSearchParams();
    if (projectIds !== void 0) {
      for (const projectId of projectIds) {
        params.append("id", projectId);
      }
    }
    if (name !== void 0) {
      params.append("name", name);
    }
    if (nameContains !== void 0) {
      params.append("name_contains", nameContains);
    }
    if (referenceDatasetId !== void 0) {
      params.append("reference_dataset", referenceDatasetId);
    } else if (referenceDatasetName !== void 0) {
      const dataset = await this.readDataset({
        datasetName: referenceDatasetName
      });
      params.append("reference_dataset", dataset.id);
    }
    if (includeStats !== void 0) {
      params.append("include_stats", includeStats.toString());
    }
    if (datasetVersion !== void 0) {
      params.append("dataset_version", datasetVersion);
    }
    if (referenceFree !== void 0) {
      params.append("reference_free", referenceFree.toString());
    }
    if (metadata !== void 0) {
      params.append("metadata", JSON.stringify(metadata));
    }
    for await (const projects of this._getPaginated("/sessions", params)) {
      yield* projects;
    }
  }
  async deleteProject({ projectId, projectName }) {
    let projectId_;
    if (projectId === void 0 && projectName === void 0) {
      throw new Error("Must provide projectName or projectId");
    } else if (projectId !== void 0 && projectName !== void 0) {
      throw new Error("Must provide either projectName or projectId, not both");
    } else if (projectId === void 0) {
      projectId_ = (await this.readProject({ projectName })).id;
    } else {
      projectId_ = projectId;
    }
    assertUuid(projectId_);
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/sessions/${projectId_}`, {
        method: "DELETE",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, `delete session ${projectId_} (${projectName})`, true);
      return res;
    });
  }
  async uploadCsv({ csvFile, fileName, inputKeys, outputKeys, description, dataType, name }) {
    const url = `${this.apiUrl}/datasets/upload`;
    const formData = new FormData();
    const csvBlob = new Blob([csvFile], { type: "text/csv" });
    formData.append("file", csvBlob, fileName);
    inputKeys.forEach((key) => {
      formData.append("input_keys", key);
    });
    outputKeys.forEach((key) => {
      formData.append("output_keys", key);
    });
    if (description) {
      formData.append("description", description);
    }
    if (dataType) {
      formData.append("data_type", dataType);
    }
    if (name) {
      formData.append("name", name);
    }
    const response = await this.caller.call(async () => {
      const res = await this._fetch(url, {
        method: "POST",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: formData
      });
      await raiseForStatus(res, "upload CSV");
      return res;
    });
    const result = await response.json();
    return result;
  }
  async createDataset(name, { description, dataType, inputsSchema, outputsSchema, metadata } = {}) {
    const body = {
      name,
      description,
      extra: { source: "sdk", ...metadata ? { metadata } : {} }
    };
    if (dataType) {
      body.data_type = dataType;
    }
    if (inputsSchema) {
      body.inputs_schema_definition = inputsSchema;
    }
    if (outputsSchema) {
      body.outputs_schema_definition = outputsSchema;
    }
    const serializedBody = JSON.stringify(body);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets`, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: serializedBody
      });
      await raiseForStatus(res, "create dataset");
      return res;
    });
    const result = await response.json();
    return result;
  }
  async readDataset({ datasetId, datasetName }) {
    let path2 = "/datasets";
    const params = new URLSearchParams({ limit: "1" });
    if (datasetId && datasetName) {
      throw new Error("Must provide either datasetName or datasetId, not both");
    } else if (datasetId) {
      assertUuid(datasetId);
      path2 += `/${datasetId}`;
    } else if (datasetName) {
      params.append("name", datasetName);
    } else {
      throw new Error("Must provide datasetName or datasetId");
    }
    const response = await this._get(path2, params);
    let result;
    if (Array.isArray(response)) {
      if (response.length === 0) {
        throw new Error(`Dataset[id=${datasetId}, name=${datasetName}] not found`);
      }
      result = response[0];
    } else {
      result = response;
    }
    return result;
  }
  async hasDataset({ datasetId, datasetName }) {
    try {
      await this.readDataset({ datasetId, datasetName });
      return true;
    } catch (e) {
      if (
        // eslint-disable-next-line no-instanceof/no-instanceof
        e instanceof Error && e.message.toLocaleLowerCase().includes("not found")
      ) {
        return false;
      }
      throw e;
    }
  }
  async diffDatasetVersions({ datasetId, datasetName, fromVersion, toVersion }) {
    let datasetId_ = datasetId;
    if (datasetId_ === void 0 && datasetName === void 0) {
      throw new Error("Must provide either datasetName or datasetId");
    } else if (datasetId_ !== void 0 && datasetName !== void 0) {
      throw new Error("Must provide either datasetName or datasetId, not both");
    } else if (datasetId_ === void 0) {
      const dataset = await this.readDataset({ datasetName });
      datasetId_ = dataset.id;
    }
    const urlParams = new URLSearchParams({
      from_version: typeof fromVersion === "string" ? fromVersion : fromVersion.toISOString(),
      to_version: typeof toVersion === "string" ? toVersion : toVersion.toISOString()
    });
    const response = await this._get(`/datasets/${datasetId_}/versions/diff`, urlParams);
    return response;
  }
  async readDatasetOpenaiFinetuning({ datasetId, datasetName }) {
    const path2 = "/datasets";
    if (datasetId !== void 0) {
    } else if (datasetName !== void 0) {
      datasetId = (await this.readDataset({ datasetName })).id;
    } else {
      throw new Error("Must provide either datasetName or datasetId");
    }
    const response = await this._getResponse(`${path2}/${datasetId}/openai_ft`);
    const datasetText = await response.text();
    const dataset = datasetText.trim().split("\n").map((line) => JSON.parse(line));
    return dataset;
  }
  async *listDatasets({ limit = 100, offset = 0, datasetIds, datasetName, datasetNameContains, metadata } = {}) {
    const path2 = "/datasets";
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    });
    if (datasetIds !== void 0) {
      for (const id_ of datasetIds) {
        params.append("id", id_);
      }
    }
    if (datasetName !== void 0) {
      params.append("name", datasetName);
    }
    if (datasetNameContains !== void 0) {
      params.append("name_contains", datasetNameContains);
    }
    if (metadata !== void 0) {
      params.append("metadata", JSON.stringify(metadata));
    }
    for await (const datasets of this._getPaginated(path2, params)) {
      yield* datasets;
    }
  }
  /**
   * Update a dataset
   * @param props The dataset details to update
   * @returns The updated dataset
   */
  async updateDataset(props) {
    const { datasetId, datasetName, ...update } = props;
    if (!datasetId && !datasetName) {
      throw new Error("Must provide either datasetName or datasetId");
    }
    const _datasetId = datasetId ?? (await this.readDataset({ datasetName })).id;
    assertUuid(_datasetId);
    const body = JSON.stringify(update);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets/${_datasetId}`, {
        method: "PATCH",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "update dataset");
      return res;
    });
    return await response.json();
  }
  /**
   * Updates a tag on a dataset.
   *
   * If the tag is already assigned to a different version of this dataset,
   * the tag will be moved to the new version. The as_of parameter is used to
   * determine which version of the dataset to apply the new tags to.
   *
   * It must be an exact version of the dataset to succeed. You can
   * use the "readDatasetVersion" method to find the exact version
   * to apply the tags to.
   * @param params.datasetId The ID of the dataset to update. Must be provided if "datasetName" is not provided.
   * @param params.datasetName The name of the dataset to update. Must be provided if "datasetId" is not provided.
   * @param params.asOf The timestamp of the dataset to apply the new tags to.
   * @param params.tag The new tag to apply to the dataset.
   */
  async updateDatasetTag(props) {
    const { datasetId, datasetName, asOf, tag } = props;
    if (!datasetId && !datasetName) {
      throw new Error("Must provide either datasetName or datasetId");
    }
    const _datasetId = datasetId ?? (await this.readDataset({ datasetName })).id;
    assertUuid(_datasetId);
    const body = JSON.stringify({
      as_of: typeof asOf === "string" ? asOf : asOf.toISOString(),
      tag
    });
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets/${_datasetId}/tags`, {
        method: "PUT",
        headers: {
          ...this._mergedHeaders,
          "Content-Type": "application/json"
        },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "update dataset tags", true);
      return res;
    });
  }
  async deleteDataset({ datasetId, datasetName }) {
    let path2 = "/datasets";
    let datasetId_ = datasetId;
    if (datasetId !== void 0 && datasetName !== void 0) {
      throw new Error("Must provide either datasetName or datasetId, not both");
    } else if (datasetName !== void 0) {
      const dataset = await this.readDataset({ datasetName });
      datasetId_ = dataset.id;
    }
    if (datasetId_ !== void 0) {
      assertUuid(datasetId_);
      path2 += `/${datasetId_}`;
    } else {
      throw new Error("Must provide datasetName or datasetId");
    }
    await this.caller.call(async () => {
      const res = await this._fetch(this.apiUrl + path2, {
        method: "DELETE",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, `delete ${path2}`, true);
      return res;
    });
  }
  async createExample(inputsOrUpdate, outputs, options) {
    if (isExampleCreate(inputsOrUpdate)) {
      if (outputs !== void 0 || options !== void 0) {
        throw new Error("Cannot provide outputs or options when using ExampleCreate object");
      }
    }
    let datasetId_ = outputs ? options?.datasetId : inputsOrUpdate.dataset_id;
    const datasetName_ = outputs ? options?.datasetName : inputsOrUpdate.dataset_name;
    if (datasetId_ === void 0 && datasetName_ === void 0) {
      throw new Error("Must provide either datasetName or datasetId");
    } else if (datasetId_ !== void 0 && datasetName_ !== void 0) {
      throw new Error("Must provide either datasetName or datasetId, not both");
    } else if (datasetId_ === void 0) {
      const dataset = await this.readDataset({ datasetName: datasetName_ });
      datasetId_ = dataset.id;
    }
    const createdAt_ = (outputs ? options?.createdAt : inputsOrUpdate.created_at) || /* @__PURE__ */ new Date();
    let data;
    if (!isExampleCreate(inputsOrUpdate)) {
      data = {
        inputs: inputsOrUpdate,
        outputs,
        created_at: createdAt_?.toISOString(),
        id: options?.exampleId,
        metadata: options?.metadata,
        split: options?.split,
        source_run_id: options?.sourceRunId,
        use_source_run_io: options?.useSourceRunIO,
        use_source_run_attachments: options?.useSourceRunAttachments,
        attachments: options?.attachments
      };
    } else {
      data = inputsOrUpdate;
    }
    const response = await this._uploadExamplesMultipart(datasetId_, [data]);
    const example = await this.readExample(response.example_ids?.[0] ?? v4_default());
    return example;
  }
  async createExamples(propsOrUploads) {
    if (Array.isArray(propsOrUploads)) {
      if (propsOrUploads.length === 0) {
        return [];
      }
      const uploads = propsOrUploads;
      let datasetId_2 = uploads[0].dataset_id;
      const datasetName_2 = uploads[0].dataset_name;
      if (datasetId_2 === void 0 && datasetName_2 === void 0) {
        throw new Error("Must provide either datasetName or datasetId");
      } else if (datasetId_2 !== void 0 && datasetName_2 !== void 0) {
        throw new Error("Must provide either datasetName or datasetId, not both");
      } else if (datasetId_2 === void 0) {
        const dataset = await this.readDataset({ datasetName: datasetName_2 });
        datasetId_2 = dataset.id;
      }
      const response2 = await this._uploadExamplesMultipart(datasetId_2, uploads);
      const examples2 = await Promise.all(response2.example_ids.map((id) => this.readExample(id)));
      return examples2;
    }
    const { inputs, outputs, metadata, splits, sourceRunIds, useSourceRunIOs, useSourceRunAttachments, attachments, exampleIds, datasetId, datasetName } = propsOrUploads;
    if (inputs === void 0) {
      throw new Error("Must provide inputs when using legacy parameters");
    }
    let datasetId_ = datasetId;
    const datasetName_ = datasetName;
    if (datasetId_ === void 0 && datasetName_ === void 0) {
      throw new Error("Must provide either datasetName or datasetId");
    } else if (datasetId_ !== void 0 && datasetName_ !== void 0) {
      throw new Error("Must provide either datasetName or datasetId, not both");
    } else if (datasetId_ === void 0) {
      const dataset = await this.readDataset({ datasetName: datasetName_ });
      datasetId_ = dataset.id;
    }
    const formattedExamples = inputs.map((input, idx) => {
      return {
        dataset_id: datasetId_,
        inputs: input,
        outputs: outputs?.[idx],
        metadata: metadata?.[idx],
        split: splits?.[idx],
        id: exampleIds?.[idx],
        attachments: attachments?.[idx],
        source_run_id: sourceRunIds?.[idx],
        use_source_run_io: useSourceRunIOs?.[idx],
        use_source_run_attachments: useSourceRunAttachments?.[idx]
      };
    });
    const response = await this._uploadExamplesMultipart(datasetId_, formattedExamples);
    const examples = await Promise.all(response.example_ids.map((id) => this.readExample(id)));
    return examples;
  }
  async createLLMExample(input, generation, options) {
    return this.createExample({ input }, { output: generation }, options);
  }
  async createChatExample(input, generations, options) {
    const finalInput = input.map((message) => {
      if (isLangChainMessage(message)) {
        return convertLangChainMessageToExample(message);
      }
      return message;
    });
    const finalOutput = isLangChainMessage(generations) ? convertLangChainMessageToExample(generations) : generations;
    return this.createExample({ input: finalInput }, { output: finalOutput }, options);
  }
  async readExample(exampleId) {
    assertUuid(exampleId);
    const path2 = `/examples/${exampleId}`;
    const rawExample = await this._get(path2);
    const { attachment_urls, ...rest } = rawExample;
    const example = rest;
    if (attachment_urls) {
      example.attachments = Object.entries(attachment_urls).reduce((acc, [key, value]) => {
        acc[key.slice("attachment.".length)] = {
          presigned_url: value.presigned_url,
          mime_type: value.mime_type
        };
        return acc;
      }, {});
    }
    return example;
  }
  async *listExamples({ datasetId, datasetName, exampleIds, asOf, splits, inlineS3Urls, metadata, limit, offset, filter, includeAttachments } = {}) {
    let datasetId_;
    if (datasetId !== void 0 && datasetName !== void 0) {
      throw new Error("Must provide either datasetName or datasetId, not both");
    } else if (datasetId !== void 0) {
      datasetId_ = datasetId;
    } else if (datasetName !== void 0) {
      const dataset = await this.readDataset({ datasetName });
      datasetId_ = dataset.id;
    } else {
      throw new Error("Must provide a datasetName or datasetId");
    }
    const params = new URLSearchParams({ dataset: datasetId_ });
    const dataset_version = asOf ? typeof asOf === "string" ? asOf : asOf?.toISOString() : void 0;
    if (dataset_version) {
      params.append("as_of", dataset_version);
    }
    const inlineS3Urls_ = inlineS3Urls ?? true;
    params.append("inline_s3_urls", inlineS3Urls_.toString());
    if (exampleIds !== void 0) {
      for (const id_ of exampleIds) {
        params.append("id", id_);
      }
    }
    if (splits !== void 0) {
      for (const split of splits) {
        params.append("splits", split);
      }
    }
    if (metadata !== void 0) {
      const serializedMetadata = JSON.stringify(metadata);
      params.append("metadata", serializedMetadata);
    }
    if (limit !== void 0) {
      params.append("limit", limit.toString());
    }
    if (offset !== void 0) {
      params.append("offset", offset.toString());
    }
    if (filter !== void 0) {
      params.append("filter", filter);
    }
    if (includeAttachments === true) {
      ["attachment_urls", "outputs", "metadata"].forEach((field) => params.append("select", field));
    }
    let i = 0;
    for await (const rawExamples of this._getPaginated("/examples", params)) {
      for (const rawExample of rawExamples) {
        const { attachment_urls, ...rest } = rawExample;
        const example = rest;
        if (attachment_urls) {
          example.attachments = Object.entries(attachment_urls).reduce((acc, [key, value]) => {
            acc[key.slice("attachment.".length)] = {
              presigned_url: value.presigned_url,
              mime_type: value.mime_type || void 0
            };
            return acc;
          }, {});
        }
        yield example;
        i++;
      }
      if (limit !== void 0 && i >= limit) {
        break;
      }
    }
  }
  async deleteExample(exampleId) {
    assertUuid(exampleId);
    const path2 = `/examples/${exampleId}`;
    await this.caller.call(async () => {
      const res = await this._fetch(this.apiUrl + path2, {
        method: "DELETE",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, `delete ${path2}`, true);
      return res;
    });
  }
  /**
   * Delete multiple examples by ID.
   * @param exampleIds - The IDs of the examples to delete
   * @param options - Optional settings for deletion
   * @param options.hardDelete - If true, permanently delete examples. If false (default), soft delete them.
   */
  async deleteExamples(exampleIds, options) {
    exampleIds.forEach((id) => assertUuid(id));
    if (options?.hardDelete) {
      const path2 = this._getPlatformEndpointPath("datasets/examples/delete");
      await this.caller.call(async () => {
        const res = await this._fetch(`${this.apiUrl}${path2}`, {
          method: "POST",
          headers: {
            ...this._mergedHeaders,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            example_ids: exampleIds,
            hard_delete: true
          }),
          signal: AbortSignal.timeout(this.timeout_ms),
          ...this.fetchOptions
        });
        await raiseForStatus(res, "hard delete examples", true);
        return res;
      });
    } else {
      const params = new URLSearchParams();
      exampleIds.forEach((id) => params.append("example_ids", id));
      await this.caller.call(async () => {
        const res = await this._fetch(`${this.apiUrl}/examples?${params.toString()}`, {
          method: "DELETE",
          headers: this._mergedHeaders,
          signal: AbortSignal.timeout(this.timeout_ms),
          ...this.fetchOptions
        });
        await raiseForStatus(res, "delete examples", true);
        return res;
      });
    }
  }
  async updateExample(exampleIdOrUpdate, update) {
    let exampleId;
    if (update) {
      exampleId = exampleIdOrUpdate;
    } else {
      exampleId = exampleIdOrUpdate.id;
    }
    assertUuid(exampleId);
    let updateToUse;
    if (update) {
      updateToUse = { id: exampleId, ...update };
    } else {
      updateToUse = exampleIdOrUpdate;
    }
    let datasetId;
    if (updateToUse.dataset_id !== void 0) {
      datasetId = updateToUse.dataset_id;
    } else {
      const example = await this.readExample(exampleId);
      datasetId = example.dataset_id;
    }
    return this._updateExamplesMultipart(datasetId, [updateToUse]);
  }
  async updateExamples(update) {
    let datasetId;
    if (update[0].dataset_id === void 0) {
      const example = await this.readExample(update[0].id);
      datasetId = example.dataset_id;
    } else {
      datasetId = update[0].dataset_id;
    }
    return this._updateExamplesMultipart(datasetId, update);
  }
  /**
   * Get dataset version by closest date or exact tag.
   *
   * Use this to resolve the nearest version to a given timestamp or for a given tag.
   *
   * @param options The options for getting the dataset version
   * @param options.datasetId The ID of the dataset
   * @param options.datasetName The name of the dataset
   * @param options.asOf The timestamp of the dataset to retrieve
   * @param options.tag The tag of the dataset to retrieve
   * @returns The dataset version
   */
  async readDatasetVersion({ datasetId, datasetName, asOf, tag }) {
    let resolvedDatasetId;
    if (!datasetId) {
      const dataset = await this.readDataset({ datasetName });
      resolvedDatasetId = dataset.id;
    } else {
      resolvedDatasetId = datasetId;
    }
    assertUuid(resolvedDatasetId);
    if (asOf && tag || !asOf && !tag) {
      throw new Error("Exactly one of asOf and tag must be specified.");
    }
    const params = new URLSearchParams();
    if (asOf !== void 0) {
      params.append("as_of", typeof asOf === "string" ? asOf : asOf.toISOString());
    }
    if (tag !== void 0) {
      params.append("tag", tag);
    }
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets/${resolvedDatasetId}/version?${params.toString()}`, {
        method: "GET",
        headers: { ...this._mergedHeaders },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "read dataset version");
      return res;
    });
    return await response.json();
  }
  async listDatasetSplits({ datasetId, datasetName, asOf }) {
    let datasetId_;
    if (datasetId === void 0 && datasetName === void 0) {
      throw new Error("Must provide dataset name or ID");
    } else if (datasetId !== void 0 && datasetName !== void 0) {
      throw new Error("Must provide either datasetName or datasetId, not both");
    } else if (datasetId === void 0) {
      const dataset = await this.readDataset({ datasetName });
      datasetId_ = dataset.id;
    } else {
      datasetId_ = datasetId;
    }
    assertUuid(datasetId_);
    const params = new URLSearchParams();
    const dataset_version = asOf ? typeof asOf === "string" ? asOf : asOf?.toISOString() : void 0;
    if (dataset_version) {
      params.append("as_of", dataset_version);
    }
    const response = await this._get(`/datasets/${datasetId_}/splits`, params);
    return response;
  }
  async updateDatasetSplits({ datasetId, datasetName, splitName, exampleIds, remove = false }) {
    let datasetId_;
    if (datasetId === void 0 && datasetName === void 0) {
      throw new Error("Must provide dataset name or ID");
    } else if (datasetId !== void 0 && datasetName !== void 0) {
      throw new Error("Must provide either datasetName or datasetId, not both");
    } else if (datasetId === void 0) {
      const dataset = await this.readDataset({ datasetName });
      datasetId_ = dataset.id;
    } else {
      datasetId_ = datasetId;
    }
    assertUuid(datasetId_);
    const data = {
      split_name: splitName,
      examples: exampleIds.map((id) => {
        assertUuid(id);
        return id;
      }),
      remove
    };
    const body = JSON.stringify(data);
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets/${datasetId_}/splits`, {
        method: "PUT",
        headers: {
          ...this._mergedHeaders,
          "Content-Type": "application/json"
        },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "update dataset splits", true);
      return res;
    });
  }
  async createFeedback(runId, key, { score, value, correction, comment, sourceInfo, feedbackSourceType = "api", sourceRunId, feedbackId, feedbackConfig, projectId, comparativeExperimentId, sessionId, startTime }) {
    if (!runId && !projectId) {
      throw new Error("One of runId or projectId must be provided");
    }
    if (runId && projectId) {
      throw new Error("Only one of runId or projectId can be provided");
    }
    const feedback_source = {
      type: feedbackSourceType ?? "api",
      metadata: sourceInfo ?? {}
    };
    if (sourceRunId !== void 0 && feedback_source?.metadata !== void 0 && !feedback_source.metadata["__run"]) {
      feedback_source.metadata["__run"] = { run_id: sourceRunId };
    }
    if (feedback_source?.metadata !== void 0 && feedback_source.metadata["__run"]?.run_id !== void 0) {
      assertUuid(feedback_source.metadata["__run"].run_id);
    }
    const feedback = {
      id: feedbackId ?? v7_default(),
      run_id: runId,
      key,
      score: _formatFeedbackScore(score),
      value,
      correction,
      comment,
      feedback_source,
      comparative_experiment_id: comparativeExperimentId,
      feedbackConfig,
      session_id: sessionId ?? projectId,
      start_time: startTime
    };
    const body = JSON.stringify(feedback);
    const url = `${this.apiUrl}/feedback`;
    await this.caller.call(async () => {
      const res = await this._fetch(url, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "create feedback", true);
      return res;
    });
    return feedback;
  }
  async updateFeedback(feedbackId, { score, value, correction, comment }) {
    const feedbackUpdate = {};
    if (score !== void 0 && score !== null) {
      feedbackUpdate["score"] = _formatFeedbackScore(score);
    }
    if (value !== void 0 && value !== null) {
      feedbackUpdate["value"] = value;
    }
    if (correction !== void 0 && correction !== null) {
      feedbackUpdate["correction"] = correction;
    }
    if (comment !== void 0 && comment !== null) {
      feedbackUpdate["comment"] = comment;
    }
    assertUuid(feedbackId);
    const body = JSON.stringify(feedbackUpdate);
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/feedback/${feedbackId}`, {
        method: "PATCH",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "update feedback", true);
      return res;
    });
  }
  async readFeedback(feedbackId) {
    assertUuid(feedbackId);
    const path2 = `/feedback/${feedbackId}`;
    const response = await this._get(path2);
    return response;
  }
  async deleteFeedback(feedbackId) {
    assertUuid(feedbackId);
    const path2 = `/feedback/${feedbackId}`;
    await this.caller.call(async () => {
      const res = await this._fetch(this.apiUrl + path2, {
        method: "DELETE",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, `delete ${path2}`, true);
      return res;
    });
  }
  async *listFeedback({ runIds, feedbackKeys, feedbackSourceTypes } = {}) {
    const queryParams = new URLSearchParams();
    if (runIds) {
      for (const runId of runIds) {
        assertUuid(runId);
        queryParams.append("run", runId);
      }
    }
    if (feedbackKeys) {
      for (const key of feedbackKeys) {
        queryParams.append("key", key);
      }
    }
    if (feedbackSourceTypes) {
      for (const type of feedbackSourceTypes) {
        queryParams.append("source", type);
      }
    }
    for await (const feedbacks of this._getPaginated("/feedback", queryParams)) {
      yield* feedbacks;
    }
  }
  /**
   * Creates a presigned feedback token and URL.
   *
   * The token can be used to authorize feedback metrics without
   * needing an API key. This is useful for giving browser-based
   * applications the ability to submit feedback without needing
   * to expose an API key.
   *
   * @param runId The ID of the run.
   * @param feedbackKey The feedback key.
   * @param options Additional options for the token.
   * @param options.expiration The expiration time for the token.
   *
   * @returns A promise that resolves to a FeedbackIngestToken.
   */
  async createPresignedFeedbackToken(runId, feedbackKey, { expiration, feedbackConfig } = {}) {
    const body = {
      run_id: runId,
      feedback_key: feedbackKey,
      feedback_config: feedbackConfig
    };
    if (expiration) {
      if (typeof expiration === "string") {
        body["expires_at"] = expiration;
      } else if (expiration?.hours || expiration?.minutes || expiration?.days) {
        body["expires_in"] = expiration;
      }
    } else {
      body["expires_in"] = {
        hours: 3
      };
    }
    const serializedBody = JSON.stringify(body);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/feedback/tokens`, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: serializedBody
      });
      await raiseForStatus(res, "create presigned feedback token");
      return res;
    });
    return await response.json();
  }
  async createComparativeExperiment({ name, experimentIds, referenceDatasetId, createdAt, description, metadata, id }) {
    if (experimentIds.length === 0) {
      throw new Error("At least one experiment is required");
    }
    if (!referenceDatasetId) {
      referenceDatasetId = (await this.readProject({
        projectId: experimentIds[0]
      })).reference_dataset_id;
    }
    if (!referenceDatasetId == null) {
      throw new Error("A reference dataset is required");
    }
    const body = {
      id,
      name,
      experiment_ids: experimentIds,
      reference_dataset_id: referenceDatasetId,
      description,
      created_at: (createdAt ?? /* @__PURE__ */ new Date())?.toISOString(),
      extra: {}
    };
    if (metadata)
      body.extra["metadata"] = metadata;
    const serializedBody = JSON.stringify(body);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/datasets/comparative`, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: serializedBody
      });
      await raiseForStatus(res, "create comparative experiment");
      return res;
    });
    return response.json();
  }
  /**
   * Retrieves a list of presigned feedback tokens for a given run ID.
   * @param runId The ID of the run.
   * @returns An async iterable of FeedbackIngestToken objects.
   */
  async *listPresignedFeedbackTokens(runId) {
    assertUuid(runId);
    const params = new URLSearchParams({ run_id: runId });
    for await (const tokens of this._getPaginated("/feedback/tokens", params)) {
      yield* tokens;
    }
  }
  _selectEvalResults(results) {
    let results_;
    if ("results" in results) {
      results_ = results.results;
    } else if (Array.isArray(results)) {
      results_ = results;
    } else {
      results_ = [results];
    }
    return results_;
  }
  async _logEvaluationFeedback(evaluatorResponse, run, sourceInfo) {
    const evalResults = this._selectEvalResults(evaluatorResponse);
    const feedbacks = [];
    for (const res of evalResults) {
      let sourceInfo_ = sourceInfo || {};
      if (res.evaluatorInfo) {
        sourceInfo_ = { ...res.evaluatorInfo, ...sourceInfo_ };
      }
      let runId_ = null;
      if (res.targetRunId) {
        runId_ = res.targetRunId;
      } else if (run) {
        runId_ = run.id;
      }
      feedbacks.push(await this.createFeedback(runId_, res.key, {
        score: res.score,
        value: res.value,
        comment: res.comment,
        correction: res.correction,
        sourceInfo: sourceInfo_,
        sourceRunId: res.sourceRunId,
        feedbackConfig: res.feedbackConfig,
        feedbackSourceType: "model",
        sessionId: run?.session_id,
        startTime: run?.start_time
      }));
    }
    return [evalResults, feedbacks];
  }
  async logEvaluationFeedback(evaluatorResponse, run, sourceInfo) {
    const [results] = await this._logEvaluationFeedback(evaluatorResponse, run, sourceInfo);
    return results;
  }
  /**
   * API for managing feedback configs
   */
  /**
   * Create a feedback configuration on the LangSmith API.
   *
   * This upserts: if an identical config already exists, it returns it.
   * If a conflicting config exists for the same key, a 400 error is raised.
   *
   * @param options - The options for creating a feedback config
   * @param options.feedbackKey - The unique key for this feedback config
   * @param options.feedbackConfig - The config specifying type, bounds, and categories
   * @param options.isLowerScoreBetter - Whether a lower score is better
   * @returns The created FeedbackConfigSchema object
   */
  async createFeedbackConfig(options) {
    const { feedbackKey, feedbackConfig, isLowerScoreBetter = false } = options;
    const body = {
      feedback_key: feedbackKey,
      feedback_config: feedbackConfig,
      is_lower_score_better: isLowerScoreBetter
    };
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/feedback-configs`, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: JSON.stringify(body)
      });
      await raiseForStatus(res, "create feedback config");
      return res;
    });
    return response.json();
  }
  /**
   * List feedback configurations on the LangSmith API.
   * @param options - The options for listing feedback configs
   * @param options.feedbackKeys - Filter by specific feedback keys
   * @param options.nameContains - Filter by name substring
   * @param options.limit - The maximum number of configs to return
   * @returns An async iterator of FeedbackConfigSchema objects
   */
  async *listFeedbackConfigs(options = {}) {
    const { feedbackKeys, nameContains, limit } = options;
    const params = new URLSearchParams();
    if (feedbackKeys) {
      feedbackKeys.forEach((key) => {
        params.append("key", key);
      });
    }
    if (nameContains)
      params.append("name_contains", nameContains);
    params.append("limit", (limit !== void 0 ? Math.min(limit, 100) : 100).toString());
    let count = 0;
    for await (const configs of this._getPaginated("/feedback-configs", params)) {
      yield* configs;
      count += configs.length;
      if (limit !== void 0 && count >= limit)
        break;
    }
  }
  /**
   * Update a feedback configuration on the LangSmith API.
   * @param feedbackKey - The key of the feedback config to update
   * @param options - The options for updating the feedback config
   * @param options.feedbackConfig - The new feedback config
   * @param options.isLowerScoreBetter - Whether a lower score is better
   * @returns The updated FeedbackConfigSchema object
   */
  async updateFeedbackConfig(feedbackKey, options = {}) {
    const { feedbackConfig, isLowerScoreBetter } = options;
    const body = { feedback_key: feedbackKey };
    if (feedbackConfig !== void 0) {
      body.feedback_config = feedbackConfig;
    }
    if (isLowerScoreBetter !== void 0) {
      body.is_lower_score_better = isLowerScoreBetter;
    }
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/feedback-configs`, {
        method: "PATCH",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: JSON.stringify(body)
      });
      await raiseForStatus(res, "update feedback config");
      return res;
    });
    return response.json();
  }
  /**
   * Delete a feedback configuration on the LangSmith API.
   * @param feedbackKey - The key of the feedback config to delete
   */
  async deleteFeedbackConfig(feedbackKey) {
    const params = new URLSearchParams({ feedback_key: feedbackKey });
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/feedback-configs?${params}`, {
        method: "DELETE",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "delete feedback config", true);
      return res;
    });
  }
  /**
   * API for managing annotation queues
   */
  /**
   * List the annotation queues on the LangSmith API.
   * @param options - The options for listing annotation queues
   * @param options.queueIds - The IDs of the queues to filter by
   * @param options.name - The name of the queue to filter by
   * @param options.nameContains - The substring that the queue name should contain
   * @param options.limit - The maximum number of queues to return
   * @returns An iterator of AnnotationQueue objects
   */
  async *listAnnotationQueues(options = {}) {
    const { queueIds, name, nameContains, limit } = options;
    const params = new URLSearchParams();
    if (queueIds) {
      queueIds.forEach((id, i) => {
        assertUuid(id, `queueIds[${i}]`);
        params.append("ids", id);
      });
    }
    if (name)
      params.append("name", name);
    if (nameContains)
      params.append("name_contains", nameContains);
    params.append("limit", (limit !== void 0 ? Math.min(limit, 100) : 100).toString());
    let count = 0;
    for await (const queues of this._getPaginated("/annotation-queues", params)) {
      yield* queues;
      count++;
      if (limit !== void 0 && count >= limit)
        break;
    }
  }
  /**
   * Create an annotation queue on the LangSmith API.
   * @param options - The options for creating an annotation queue
   * @param options.name - The name of the annotation queue
   * @param options.description - The description of the annotation queue
   * @param options.queueId - The ID of the annotation queue
   * @returns The created AnnotationQueue object
   */
  async createAnnotationQueue(options) {
    const { name, description, queueId, rubricInstructions, rubricItems } = options;
    const body = {
      name,
      description,
      id: queueId || v4_default(),
      rubric_instructions: rubricInstructions,
      rubric_items: rubricItems
    };
    const serializedBody = JSON.stringify(Object.fromEntries(Object.entries(body).filter(([_, v]) => v !== void 0)));
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/annotation-queues`, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: serializedBody
      });
      await raiseForStatus(res, "create annotation queue");
      return res;
    });
    return response.json();
  }
  /**
   * Read an annotation queue with the specified queue ID.
   * @param queueId - The ID of the annotation queue to read
   * @returns The AnnotationQueueWithDetails object
   */
  async readAnnotationQueue(queueId) {
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/annotation-queues/${assertUuid(queueId, "queueId")}`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "read annotation queue");
      return res;
    });
    return response.json();
  }
  /**
   * Update an annotation queue with the specified queue ID.
   * @param queueId - The ID of the annotation queue to update
   * @param options - The options for updating the annotation queue
   * @param options.name - The new name for the annotation queue
   * @param options.description - The new description for the annotation queue
   */
  async updateAnnotationQueue(queueId, options) {
    const { name, description, rubricInstructions, rubricItems } = options;
    const bodyObj = {};
    if (name !== void 0)
      bodyObj.name = name;
    if (description !== void 0)
      bodyObj.description = description;
    if (rubricInstructions !== void 0)
      bodyObj.rubric_instructions = rubricInstructions;
    if (rubricItems !== void 0)
      bodyObj.rubric_items = rubricItems;
    const body = JSON.stringify(bodyObj);
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/annotation-queues/${assertUuid(queueId, "queueId")}`, {
        method: "PATCH",
        headers: {
          ...this._mergedHeaders,
          "Content-Type": "application/json"
        },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "update annotation queue", true);
      return res;
    });
  }
  /**
   * Delete an annotation queue with the specified queue ID.
   * @param queueId - The ID of the annotation queue to delete
   */
  async deleteAnnotationQueue(queueId) {
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/annotation-queues/${assertUuid(queueId, "queueId")}`, {
        method: "DELETE",
        headers: { ...this._mergedHeaders, Accept: "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "delete annotation queue", true);
      return res;
    });
  }
  /**
   * Add runs to an annotation queue with the specified queue ID.
   * @param queueId - The ID of the annotation queue
   * @param runIds - The IDs of the runs to be added to the annotation queue
   */
  async addRunsToAnnotationQueue(queueId, runIds) {
    const body = JSON.stringify(runIds.map((id, i) => assertUuid(id, `runIds[${i}]`).toString()));
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/annotation-queues/${assertUuid(queueId, "queueId")}/runs`, {
        method: "POST",
        headers: {
          ...this._mergedHeaders,
          "Content-Type": "application/json"
        },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "add runs to annotation queue", true);
      return res;
    });
  }
  /**
   * Get a run from an annotation queue at the specified index.
   * @param queueId - The ID of the annotation queue
   * @param index - The index of the run to retrieve
   * @returns A Promise that resolves to a RunWithAnnotationQueueInfo object
   * @throws {Error} If the run is not found at the given index or for other API-related errors
   */
  async getRunFromAnnotationQueue(queueId, index) {
    const baseUrl = `/annotation-queues/${assertUuid(queueId, "queueId")}/run`;
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}${baseUrl}/${index}`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "get run from annotation queue");
      return res;
    });
    const run = await response.json();
    return _normalizeRunTimestamps(run);
  }
  /**
   * Delete a run from an an annotation queue.
   * @param queueId - The ID of the annotation queue to delete the run from
   * @param queueRunId - The ID of the run to delete from the annotation queue
   */
  async deleteRunFromAnnotationQueue(queueId, queueRunId) {
    await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/annotation-queues/${assertUuid(queueId, "queueId")}/runs/${assertUuid(queueRunId, "queueRunId")}`, {
        method: "DELETE",
        headers: { ...this._mergedHeaders, Accept: "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "delete run from annotation queue", true);
      return res;
    });
  }
  /**
   * Get the size of an annotation queue.
   * @param queueId - The ID of the annotation queue
   */
  async getSizeFromAnnotationQueue(queueId) {
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/annotation-queues/${assertUuid(queueId, "queueId")}/size`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "get size from annotation queue");
      return res;
    });
    return response.json();
  }
  async _currentTenantIsOwner(owner) {
    const settings = await this._getSettings();
    return owner == "-" || settings.tenant_handle === owner;
  }
  async _ownerConflictError(action, owner) {
    const settings = await this._getSettings();
    return new Error(`Cannot ${action} for another tenant.

      Current tenant: ${settings.tenant_handle}

      Requested tenant: ${owner}`);
  }
  async _getLatestCommitHash(promptOwnerAndName) {
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/commits/${promptOwnerAndName}/?limit=${1}&offset=${0}`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "get latest commit hash");
      return res;
    });
    const json = await response.json();
    if (json.commits.length === 0) {
      return void 0;
    }
    return json.commits[0].commit_hash;
  }
  async _likeOrUnlikePrompt(promptIdentifier, like) {
    const [owner, promptName, _] = parsePromptIdentifier(promptIdentifier);
    const body = JSON.stringify({ like });
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/likes/${owner}/${promptName}`, {
        method: "POST",
        headers: {
          ...this._mergedHeaders,
          "Content-Type": "application/json"
        },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, `${like ? "like" : "unlike"} prompt`);
      return res;
    });
    return response.json();
  }
  async _getPromptUrl(promptIdentifier) {
    const [owner, promptName, commitHash] = parsePromptIdentifier(promptIdentifier);
    if (!await this._currentTenantIsOwner(owner)) {
      if (commitHash !== "latest") {
        return `${this.getHostUrl()}/hub/${owner}/${promptName}/${commitHash.substring(0, 8)}`;
      } else {
        return `${this.getHostUrl()}/hub/${owner}/${promptName}`;
      }
    } else {
      const settings = await this._getSettings();
      if (commitHash !== "latest") {
        return `${this.getHostUrl()}/prompts/${promptName}/${commitHash.substring(0, 8)}?organizationId=${settings.id}`;
      } else {
        return `${this.getHostUrl()}/prompts/${promptName}?organizationId=${settings.id}`;
      }
    }
  }
  /**
   * Check if a prompt exists.
   * @param promptIdentifier - The identifier of the prompt. Can be in the format:
   *   - "promptName" (for private prompts, owner defaults to "-")
   *   - "owner/promptName" (for prompts with explicit owner)
   * @returns A Promise that resolves to true if the prompt exists, false otherwise
   * @example
   * ```typescript
   * // Check if a prompt exists before creating a commit
   * if (await client.promptExists("my-prompt")) {
   *   await client.createCommit("my-prompt", template);
   * } else {
   *   await client.createPrompt("my-prompt");
   * }
   * ```
   */
  async promptExists(promptIdentifier) {
    const prompt = await this.getPrompt(promptIdentifier);
    return !!prompt;
  }
  /**
   * Like a prompt.
   * @param promptIdentifier - The identifier of the prompt. Can be in the format:
   *   - "promptName" (for private prompts, owner defaults to "-")
   *   - "owner/promptName" (for prompts with explicit owner)
   * @returns A Promise that resolves to the like response containing the updated like count
   * @example
   * ```typescript
   * // Like a prompt
   * const response = await client.likePrompt("owner/useful-prompt");
   * console.log(`Prompt now has ${response.likes} likes`);
   * ```
   */
  async likePrompt(promptIdentifier) {
    return this._likeOrUnlikePrompt(promptIdentifier, true);
  }
  /**
   * Unlike a prompt (remove a previously added like).
   * @param promptIdentifier - The identifier of the prompt. Can be in the format:
   *   - "promptName" (for private prompts, owner defaults to "-")
   *   - "owner/promptName" (for prompts with explicit owner)
   * @returns A Promise that resolves to the like response containing the updated like count
   * @example
   * ```typescript
   * // Unlike a prompt
   * const response = await client.unlikePrompt("owner/useful-prompt");
   * console.log(`Prompt now has ${response.likes} likes`);
   * ```
   */
  async unlikePrompt(promptIdentifier) {
    return this._likeOrUnlikePrompt(promptIdentifier, false);
  }
  /**
   * List all commits for a prompt.
   * @param promptIdentifier - The identifier of the prompt. Can be in the format:
   *   - "promptName" (for private prompts, owner defaults to "-")
   *   - "owner/promptName" (for prompts with explicit owner)
   *   - "promptName:commitHash" (commit hash is ignored, all commits are returned)
   * @returns An async iterable iterator of PromptCommit objects
   * @example
   * ```typescript
   * // List commits for a private prompt
   * for await (const commit of client.listCommits("my-prompt")) {
   *   console.log(commit);
   * }
   *
   * // List commits for a prompt with explicit owner
   * for await (const commit of client.listCommits("owner/my-prompt")) {
   *   console.log(commit);
   * }
   * ```
   */
  async *listCommits(promptIdentifier) {
    const [owner, promptName, _] = parsePromptIdentifier(promptIdentifier);
    for await (const commits of this._getPaginated(`/commits/${owner}/${promptName}/`, new URLSearchParams(), (res) => res.commits)) {
      yield* commits;
    }
  }
  /**
   * List prompts by filter.
   * @param options - Optional filters for listing prompts
   * @param options.isPublic - Filter by public/private prompts. If undefined, returns all prompts.
   * @param options.isArchived - Filter by archived status. Defaults to false (non-archived prompts only).
   * @param options.sortField - Field to sort by. Defaults to "updated_at".
   * @param options.query - Search query to filter prompts by name or description.
   * @returns An async iterable iterator of Prompt objects
   * @example
   * ```typescript
   * // List all prompts
   * for await (const prompt of client.listPrompts()) {
   *   console.log(prompt);
   * }
   *
   * // List only public prompts
   * for await (const prompt of client.listPrompts({ isPublic: true })) {
   *   console.log(prompt);
   * }
   *
   * // Search for prompts
   * for await (const prompt of client.listPrompts({ query: "translation" })) {
   *   console.log(prompt);
   * }
   * ```
   */
  async *listPrompts(options) {
    const params = new URLSearchParams();
    params.append("sort_field", options?.sortField ?? "updated_at");
    params.append("sort_direction", "desc");
    params.append("is_archived", (!!options?.isArchived).toString());
    if (options?.isPublic !== void 0) {
      params.append("is_public", options.isPublic.toString());
    }
    if (options?.query) {
      params.append("query", options.query);
    }
    for await (const prompts of this._getPaginated("/repos", params, (res) => res.repos)) {
      yield* prompts;
    }
  }
  /**
   * Get a prompt by its identifier.
   * @param promptIdentifier - The identifier of the prompt. Can be in the format:
   *   - "promptName" (for private prompts, owner defaults to "-")
   *   - "owner/promptName" (for prompts with explicit owner)
   *   - "promptName:commitHash" (commit hash is ignored, latest version is returned)
   * @returns A Promise that resolves to the Prompt object, or null if not found
   * @example
   * ```typescript
   * // Get a private prompt
   * const prompt = await client.getPrompt("my-prompt");
   *
   * // Get a public prompt
   * const publicPrompt = await client.getPrompt("owner/public-prompt");
   * ```
   */
  async getPrompt(promptIdentifier) {
    const [owner, promptName, _] = parsePromptIdentifier(promptIdentifier);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/repos/${owner}/${promptName}`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      if (res?.status === 404) {
        return null;
      }
      await raiseForStatus(res, "get prompt");
      return res;
    });
    const result = await response?.json();
    if (result?.repo) {
      return result.repo;
    } else {
      return null;
    }
  }
  /**
   * Create a new prompt.
   * @param promptIdentifier - The identifier for the new prompt. Can be in the format:
   *   - "promptName" (creates a private prompt)
   *   - "owner/promptName" (creates a prompt under a specific owner, must match your tenant)
   * @param options - Optional configuration for the prompt
   * @param options.description - A description of the prompt
   * @param options.readme - Markdown content for the prompt's README
   * @param options.tags - Array of tags to categorize the prompt
   * @param options.isPublic - Whether the prompt should be public. Requires a LangChain Hub handle.
   * @returns A Promise that resolves to the created Prompt object
   * @throws {Error} If creating a public prompt without a LangChain Hub handle, or if owner doesn't match current tenant
   * @example
   * ```typescript
   * // Create a private prompt
   * const prompt = await client.createPrompt("my-new-prompt", {
   *   description: "A prompt for translations",
   *   tags: ["translation", "language"]
   * });
   *
   * // Create a public prompt
   * const publicPrompt = await client.createPrompt("my-public-prompt", {
   *   description: "A public translation prompt",
   *   isPublic: true
   * });
   * ```
   */
  async createPrompt(promptIdentifier, options) {
    const settings = await this._getSettings();
    if (options?.isPublic && !settings.tenant_handle) {
      throw new Error(`Cannot create a public prompt without first

        creating a LangChain Hub handle.
        You can add a handle by creating a public prompt at:

        https://smith.langchain.com/prompts`);
    }
    const [owner, promptName, _] = parsePromptIdentifier(promptIdentifier);
    if (!await this._currentTenantIsOwner(owner)) {
      throw await this._ownerConflictError("create a prompt", owner);
    }
    const data = {
      repo_handle: promptName,
      ...options?.description && { description: options.description },
      ...options?.readme && { readme: options.readme },
      ...options?.tags && { tags: options.tags },
      is_public: !!options?.isPublic
    };
    const body = JSON.stringify(data);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/repos/`, {
        method: "POST",
        headers: { ...this._mergedHeaders, "Content-Type": "application/json" },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "create prompt");
      return res;
    });
    const { repo } = await response.json();
    return repo;
  }
  /**
   * Create a new commit for an existing prompt.
   * @param promptIdentifier - The identifier of the prompt. Can be in the format:
   *   - "promptName" (for private prompts, owner defaults to "-")
   *   - "owner/promptName" (for prompts with explicit owner)
   * @param object - The prompt object/manifest to commit (e.g., ChatPromptTemplate, messages array, etc.)
   * @param options - Optional configuration for the commit
   * @param options.parentCommitHash - The parent commit hash. Defaults to "latest" (the most recent commit).
   * @returns A Promise that resolves to the URL of the newly created commit
   * @throws {Error} If the prompt does not exist
   * @example
   * ```typescript
   * import { ChatPromptTemplate } from "@langchain/core/prompts";
   *
   * // Create a commit with a new version of the prompt
   * const template = ChatPromptTemplate.fromMessages([
   *   ["system", "You are a helpful assistant."],
   *   ["human", "{input}"]
   * ]);
   *
   * const commitUrl = await client.createCommit("my-prompt", template);
   * console.log(`Commit created: ${commitUrl}`);
   *
   * // Create a commit based on a specific parent commit
   * const commitUrl2 = await client.createCommit("my-prompt", template, {
   *   parentCommitHash: "abc123def456"
   * });
   * ```
   */
  async createCommit(promptIdentifier, object, options) {
    if (!await this.promptExists(promptIdentifier)) {
      throw new Error("Prompt does not exist, you must create it first.");
    }
    const [owner, promptName, _] = parsePromptIdentifier(promptIdentifier);
    const resolvedParentCommitHash = options?.parentCommitHash === "latest" || !options?.parentCommitHash ? await this._getLatestCommitHash(`${owner}/${promptName}`) : options?.parentCommitHash;
    const payload = {
      manifest: JSON.parse(JSON.stringify(object)),
      parent_commit: resolvedParentCommitHash,
      ...options?.description !== void 0 && {
        description: options.description
      }
    };
    const body = JSON.stringify(payload);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/commits/${owner}/${promptName}`, {
        method: "POST",
        headers: {
          ...this._mergedHeaders,
          "Content-Type": "application/json"
        },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "create commit");
      return res;
    });
    const result = await response.json();
    return this._getPromptUrl(`${owner}/${promptName}${result.commit_hash ? `:${result.commit_hash}` : ""}`);
  }
  /**
   * Update examples with attachments using multipart form data.
   * @param updates List of ExampleUpdateWithAttachments objects to upsert
   * @returns Promise with the update response
   */
  async updateExamplesMultipart(datasetId, updates = []) {
    return this._updateExamplesMultipart(datasetId, updates);
  }
  async _updateExamplesMultipart(datasetId, updates = []) {
    if (!await this._getDatasetExamplesMultiPartSupport()) {
      throw new Error("Your LangSmith deployment does not allow using the multipart examples endpoint, please upgrade your deployment to the latest version.");
    }
    const formData = new FormData();
    for (const example of updates) {
      const exampleId = example.id;
      const exampleBody = {
        ...example.metadata && { metadata: example.metadata },
        ...example.split && { split: example.split }
      };
      const stringifiedExample = serialize(exampleBody, `Serializing body for example with id: ${exampleId}`);
      const exampleBlob = new Blob([stringifiedExample], {
        type: "application/json"
      });
      formData.append(exampleId, exampleBlob);
      if (example.inputs) {
        const stringifiedInputs = serialize(example.inputs, `Serializing inputs for example with id: ${exampleId}`);
        const inputsBlob = new Blob([stringifiedInputs], {
          type: "application/json"
        });
        formData.append(`${exampleId}.inputs`, inputsBlob);
      }
      if (example.outputs) {
        const stringifiedOutputs = serialize(example.outputs, `Serializing outputs whle updating example with id: ${exampleId}`);
        const outputsBlob = new Blob([stringifiedOutputs], {
          type: "application/json"
        });
        formData.append(`${exampleId}.outputs`, outputsBlob);
      }
      if (example.attachments) {
        for (const [name, attachment] of Object.entries(example.attachments)) {
          let mimeType;
          let data;
          if (Array.isArray(attachment)) {
            [mimeType, data] = attachment;
          } else {
            mimeType = attachment.mimeType;
            data = attachment.data;
          }
          const attachmentBlob = new Blob([data], {
            type: `${mimeType}; length=${data.byteLength}`
          });
          formData.append(`${exampleId}.attachment.${name}`, attachmentBlob);
        }
      }
      if (example.attachments_operations) {
        const stringifiedAttachmentsOperations = serialize(example.attachments_operations, `Serializing attachments while updating example with id: ${exampleId}`);
        const attachmentsOperationsBlob = new Blob([stringifiedAttachmentsOperations], {
          type: "application/json"
        });
        formData.append(`${exampleId}.attachments_operations`, attachmentsOperationsBlob);
      }
    }
    const datasetIdToUse = datasetId ?? updates[0]?.dataset_id;
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}${this._getPlatformEndpointPath(`datasets/${datasetIdToUse}/examples`)}`, {
        method: "PATCH",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: formData
      });
      await raiseForStatus(res, "update examples");
      return res;
    });
    return response.json();
  }
  /**
   * Upload examples with attachments using multipart form data.
   * @param uploads List of ExampleUploadWithAttachments objects to upload
   * @returns Promise with the upload response
   * @deprecated This method is deprecated and will be removed in future LangSmith versions, please use `createExamples` instead
   */
  async uploadExamplesMultipart(datasetId, uploads = []) {
    return this._uploadExamplesMultipart(datasetId, uploads);
  }
  async _uploadExamplesMultipart(datasetId, uploads = []) {
    if (!await this._getDatasetExamplesMultiPartSupport()) {
      throw new Error("Your LangSmith deployment does not allow using the multipart examples endpoint, please upgrade your deployment to the latest version.");
    }
    const formData = new FormData();
    for (const example of uploads) {
      const exampleId = (example.id ?? v4_default()).toString();
      const exampleBody = {
        created_at: example.created_at,
        ...example.metadata && { metadata: example.metadata },
        ...example.split && { split: example.split },
        ...example.source_run_id && { source_run_id: example.source_run_id },
        ...example.use_source_run_io && {
          use_source_run_io: example.use_source_run_io
        },
        ...example.use_source_run_attachments && {
          use_source_run_attachments: example.use_source_run_attachments
        }
      };
      const stringifiedExample = serialize(exampleBody, `Serializing body for uploaded example with id: ${exampleId}`);
      const exampleBlob = new Blob([stringifiedExample], {
        type: "application/json"
      });
      formData.append(exampleId, exampleBlob);
      if (example.inputs) {
        const stringifiedInputs = serialize(example.inputs, `Serializing inputs for uploaded example with id: ${exampleId}`);
        const inputsBlob = new Blob([stringifiedInputs], {
          type: "application/json"
        });
        formData.append(`${exampleId}.inputs`, inputsBlob);
      }
      if (example.outputs) {
        const stringifiedOutputs = serialize(example.outputs, `Serializing outputs for uploaded example with id: ${exampleId}`);
        const outputsBlob = new Blob([stringifiedOutputs], {
          type: "application/json"
        });
        formData.append(`${exampleId}.outputs`, outputsBlob);
      }
      if (example.attachments) {
        for (const [name, attachment] of Object.entries(example.attachments)) {
          let mimeType;
          let data;
          if (Array.isArray(attachment)) {
            [mimeType, data] = attachment;
          } else {
            mimeType = attachment.mimeType;
            data = attachment.data;
          }
          const attachmentBlob = new Blob([data], {
            type: `${mimeType}; length=${data.byteLength}`
          });
          formData.append(`${exampleId}.attachment.${name}`, attachmentBlob);
        }
      }
    }
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}${this._getPlatformEndpointPath(`datasets/${datasetId}/examples`)}`, {
        method: "POST",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body: formData
      });
      await raiseForStatus(res, "upload examples");
      return res;
    });
    return response.json();
  }
  async updatePrompt(promptIdentifier, options) {
    if (!await this.promptExists(promptIdentifier)) {
      throw new Error("Prompt does not exist, you must create it first.");
    }
    const [owner, promptName] = parsePromptIdentifier(promptIdentifier);
    if (!await this._currentTenantIsOwner(owner)) {
      throw await this._ownerConflictError("update a prompt", owner);
    }
    const payload = {};
    if (options?.description !== void 0)
      payload.description = options.description;
    if (options?.readme !== void 0)
      payload.readme = options.readme;
    if (options?.tags !== void 0)
      payload.tags = options.tags;
    if (options?.isPublic !== void 0)
      payload.is_public = options.isPublic;
    if (options?.isArchived !== void 0)
      payload.is_archived = options.isArchived;
    if (Object.keys(payload).length === 0) {
      throw new Error("No valid update options provided");
    }
    const body = JSON.stringify(payload);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/repos/${owner}/${promptName}`, {
        method: "PATCH",
        headers: {
          ...this._mergedHeaders,
          "Content-Type": "application/json"
        },
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions,
        body
      });
      await raiseForStatus(res, "update prompt");
      return res;
    });
    return response.json();
  }
  async deletePrompt(promptIdentifier) {
    if (!await this.promptExists(promptIdentifier)) {
      throw new Error("Prompt does not exist, you must create it first.");
    }
    const [owner, promptName, _] = parsePromptIdentifier(promptIdentifier);
    if (!await this._currentTenantIsOwner(owner)) {
      throw await this._ownerConflictError("delete a prompt", owner);
    }
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/repos/${owner}/${promptName}`, {
        method: "DELETE",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "delete prompt");
      return res;
    });
    return response.json();
  }
  /**
   * Generate a cache key for a prompt.
   * Format: "{identifier}" or "{identifier}:with_model"
   */
  _getPromptCacheKey(promptIdentifier, includeModel) {
    const suffix = includeModel ? ":with_model" : "";
    return `${promptIdentifier}${suffix}`;
  }
  /**
   * Fetch a prompt commit directly from the API (bypassing cache).
   */
  async _fetchPromptFromApi(promptIdentifier, options) {
    const [owner, promptName, commitHash] = parsePromptIdentifier(promptIdentifier);
    const response = await this.caller.call(async () => {
      const res = await this._fetch(`${this.apiUrl}/commits/${owner}/${promptName}/${commitHash}${options?.includeModel ? "?include_model=true" : ""}`, {
        method: "GET",
        headers: this._mergedHeaders,
        signal: AbortSignal.timeout(this.timeout_ms),
        ...this.fetchOptions
      });
      await raiseForStatus(res, "pull prompt commit");
      return res;
    });
    const result = await response.json();
    return {
      owner,
      repo: promptName,
      commit_hash: result.commit_hash,
      manifest: result.manifest,
      examples: result.examples
    };
  }
  async pullPromptCommit(promptIdentifier, options) {
    const refreshFunc = this._fetchPromptFromApi.bind(this, promptIdentifier, options);
    if (!options?.skipCache && this._promptCache) {
      const cacheKey = this._getPromptCacheKey(promptIdentifier, options?.includeModel);
      const cached = this._promptCache.get(cacheKey, refreshFunc);
      if (cached) {
        return cached;
      }
      const result = await refreshFunc();
      this._promptCache.set(cacheKey, result, refreshFunc);
      return result;
    }
    return this._fetchPromptFromApi(promptIdentifier, options);
  }
  /**
   * This method should not be used directly, use `import { pull } from "langchain/hub"` instead.
   * Using this method directly returns the JSON string of the prompt rather than a LangChain object.
   * @private
   */
  async _pullPrompt(promptIdentifier, options) {
    const promptObject = await this.pullPromptCommit(promptIdentifier, {
      includeModel: options?.includeModel,
      skipCache: options?.skipCache
    });
    const prompt = JSON.stringify(promptObject.manifest);
    return prompt;
  }
  async pushPrompt(promptIdentifier, options) {
    if (await this.promptExists(promptIdentifier)) {
      if (options && Object.keys(options).some((key) => key !== "object")) {
        await this.updatePrompt(promptIdentifier, {
          description: options?.description,
          readme: options?.readme,
          tags: options?.tags,
          isPublic: options?.isPublic
        });
      }
    } else {
      await this.createPrompt(promptIdentifier, {
        description: options?.description,
        readme: options?.readme,
        tags: options?.tags,
        isPublic: options?.isPublic
      });
    }
    if (!options?.object) {
      return await this._getPromptUrl(promptIdentifier);
    }
    const url = await this.createCommit(promptIdentifier, options?.object, {
      parentCommitHash: options?.parentCommitHash,
      description: options?.commitDescription
    });
    return url;
  }
  /**
     * Clone a public dataset to your own langsmith tenant.
     * This operation is idempotent. If you already have a dataset with the given name,
     * this function will do nothing.
  
     * @param {string} tokenOrUrl The token of the public dataset to clone.
     * @param {Object} [options] Additional options for cloning the dataset.
     * @param {string} [options.sourceApiUrl] The URL of the langsmith server where the data is hosted. Defaults to the API URL of your current client.
     * @param {string} [options.datasetName] The name of the dataset to create in your tenant. Defaults to the name of the public dataset.
     * @returns {Promise<void>}
     */
  async clonePublicDataset(tokenOrUrl, options = {}) {
    const { sourceApiUrl = this.apiUrl, datasetName } = options;
    const [parsedApiUrl, tokenUuid] = this.parseTokenOrUrl(tokenOrUrl, sourceApiUrl);
    const sourceClient = new _Client({
      apiUrl: parsedApiUrl,
      // Placeholder API key not needed anymore in most cases, but
      // some private deployments may have API key-based rate limiting
      // that would cause this to fail if we provide no value.
      apiKey: "placeholder"
    });
    const ds = await sourceClient.readSharedDataset(tokenUuid);
    const finalDatasetName = datasetName || ds.name;
    try {
      if (await this.hasDataset({ datasetId: finalDatasetName })) {
        console.log(`Dataset ${finalDatasetName} already exists in your tenant. Skipping.`);
        return;
      }
    } catch (_) {
    }
    const examples = await sourceClient.listSharedExamples(tokenUuid);
    const dataset = await this.createDataset(finalDatasetName, {
      description: ds.description,
      dataType: ds.data_type || "kv",
      inputsSchema: ds.inputs_schema_definition ?? void 0,
      outputsSchema: ds.outputs_schema_definition ?? void 0
    });
    try {
      await this.createExamples({
        inputs: examples.map((e) => e.inputs),
        outputs: examples.flatMap((e) => e.outputs ? [e.outputs] : []),
        datasetId: dataset.id
      });
    } catch (e) {
      console.error(`An error occurred while creating dataset ${finalDatasetName}. You should delete it manually.`);
      throw e;
    }
  }
  parseTokenOrUrl(urlOrToken, apiUrl, numParts = 2, kind = "dataset") {
    try {
      assertUuid(urlOrToken);
      return [apiUrl, urlOrToken];
    } catch (_) {
    }
    try {
      const parsedUrl = new URL(urlOrToken);
      const pathParts = parsedUrl.pathname.split("/").filter((part) => part !== "");
      if (pathParts.length >= numParts) {
        const tokenUuid = pathParts[pathParts.length - numParts];
        return [apiUrl, tokenUuid];
      } else {
        throw new Error(`Invalid public ${kind} URL: ${urlOrToken}`);
      }
    } catch (error2) {
      throw new Error(`Invalid public ${kind} URL or token: ${urlOrToken}`);
    }
  }
  /**
   * Cleanup resources held by the client.
   * Stops the cache's background refresh timer.
   */
  cleanup() {
    if (this._promptCache) {
      this._promptCache.stop();
    }
  }
  /**
   * Awaits all pending trace batches. Useful for environments where
   * you need to be sure that all tracing requests finish before execution ends,
   * such as serverless environments.
   *
   * @example
   * ```
   * import { Client } from "langsmith";
   *
   * const client = new Client();
   *
   * try {
   *   // Tracing happens here
   *   ...
   * } finally {
   *   await client.awaitPendingTraceBatches();
   * }
   * ```
   *
   * @returns A promise that resolves once all currently pending traces have sent.
   */
  async awaitPendingTraceBatches() {
    if (this.manualFlushMode) {
      console.warn("[WARNING]: When tracing in manual flush mode, you must call `await client.flush()` manually to submit trace batches.");
      return Promise.resolve();
    }
    await new Promise((resolve) => setTimeout(resolve, 1));
    await Promise.all([
      ...this.autoBatchQueue.items.map(({ itemPromise }) => itemPromise),
      this.batchIngestCaller.queue.onIdle()
    ]);
    if (this.langSmithToOTELTranslator !== void 0) {
      await getDefaultOTLPTracerComponents()?.DEFAULT_LANGSMITH_SPAN_PROCESSOR?.forceFlush();
    }
  }
};
Object.defineProperty(Client, "_fallbackDirsCreated", {
  enumerable: true,
  configurable: true,
  writable: true,
  value: /* @__PURE__ */ new Set()
});
function isExampleCreate(input) {
  return "dataset_id" in input || "dataset_name" in input;
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/env.js
var isTracingEnabled = (tracingEnabled) => {
  if (tracingEnabled !== void 0) {
    return tracingEnabled;
  }
  const envVars = ["TRACING_V2", "TRACING"];
  return !!envVars.find((envVar) => getLangSmithEnvironmentVariable(envVar) === "true");
};

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/singletons/constants.js
var _LC_CONTEXT_VARIABLES_KEY = /* @__PURE__ */ Symbol.for("lc:context_variables");
var _REPLICA_TRACE_ROOTS_KEY = /* @__PURE__ */ Symbol.for("langsmith:replica_trace_roots");

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/context_vars.js
function getContextVar(runTree, key) {
  if (_LC_CONTEXT_VARIABLES_KEY in runTree) {
    const contextVars = runTree[_LC_CONTEXT_VARIABLES_KEY];
    return contextVars[key];
  }
  return void 0;
}
function setContextVar(runTree, key, value) {
  const contextVars = _LC_CONTEXT_VARIABLES_KEY in runTree ? (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    runTree[_LC_CONTEXT_VARIABLES_KEY]
  ) : {};
  contextVars[key] = value;
  runTree[_LC_CONTEXT_VARIABLES_KEY] = contextVars;
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/utils/project.js
var getDefaultProjectName = () => {
  return getLangSmithEnvironmentVariable("PROJECT") ?? getEnvironmentVariable("LANGCHAIN_SESSION") ?? // TODO: Deprecate
  "default";
};

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/run_trees.js
var TIMESTAMP_LENGTH = 36;
var UUID_NAMESPACE_DNS = "6ba7b810-9dad-11d1-80b4-00c04fd430c8";
function getReplicaKey(replica) {
  const sortedKeys = Object.keys(replica).sort();
  const keyData = sortedKeys.map((key) => `${key}:${replica[key] ?? ""}`).join("|");
  return v5_default(keyData, UUID_NAMESPACE_DNS);
}
function stripNonAlphanumeric(input) {
  return input.replace(/[-:.]/g, "");
}
function getMicrosecondPrecisionDatestring(epoch, executionOrder = 1) {
  const paddedOrder = executionOrder.toFixed(0).slice(0, 3).padStart(3, "0");
  return `${new Date(epoch).toISOString().slice(0, -1)}${paddedOrder}Z`;
}
function convertToDottedOrderFormat(epoch, runId, executionOrder = 1) {
  const microsecondPrecisionDatestring = getMicrosecondPrecisionDatestring(epoch, executionOrder);
  return {
    dottedOrder: stripNonAlphanumeric(microsecondPrecisionDatestring) + runId,
    microsecondPrecisionDatestring
  };
}
var HEADER_SAFE_REPLICA_FIELDS = /* @__PURE__ */ new Set([
  "projectName",
  "updates",
  "reroot"
]);
function filterReplicaForHeaders(replica) {
  const filtered = {};
  for (const key of Object.keys(replica)) {
    if (HEADER_SAFE_REPLICA_FIELDS.has(key)) {
      filtered[key] = replica[key];
    }
  }
  return filtered;
}
var Baggage = class _Baggage {
  constructor(metadata, tags, project_name, replicas2) {
    Object.defineProperty(this, "metadata", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "tags", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "project_name", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "replicas", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    this.metadata = metadata;
    this.tags = tags;
    this.project_name = project_name;
    this.replicas = replicas2;
  }
  static fromHeader(value) {
    const items = value.split(",");
    let metadata = {};
    let tags = [];
    let project_name;
    let replicas2;
    for (const item of items) {
      const [key, uriValue] = item.split("=");
      const value2 = decodeURIComponent(uriValue);
      if (key === "langsmith-metadata") {
        metadata = JSON.parse(value2);
      } else if (key === "langsmith-tags") {
        tags = value2.split(",");
      } else if (key === "langsmith-project") {
        project_name = value2;
      } else if (key === "langsmith-replicas") {
        const parsed = JSON.parse(value2);
        replicas2 = parsed.map((replica) => {
          if (Array.isArray(replica)) {
            return replica;
          }
          return filterReplicaForHeaders(replica);
        });
      }
    }
    return new _Baggage(metadata, tags, project_name, replicas2);
  }
  toHeader() {
    const items = [];
    if (this.metadata && Object.keys(this.metadata).length > 0) {
      items.push(`langsmith-metadata=${encodeURIComponent(JSON.stringify(this.metadata))}`);
    }
    if (this.tags && this.tags.length > 0) {
      items.push(`langsmith-tags=${encodeURIComponent(this.tags.join(","))}`);
    }
    if (this.project_name) {
      items.push(`langsmith-project=${encodeURIComponent(this.project_name)}`);
    }
    return items.join(",");
  }
};
var RunTree = class _RunTree {
  constructor(originalConfig) {
    Object.defineProperty(this, "id", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "name", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "run_type", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "project_name", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "parent_run", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "parent_run_id", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "child_runs", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "start_time", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "end_time", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "extra", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "tags", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "error", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "serialized", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "inputs", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "outputs", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "reference_example_id", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "client", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "events", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "trace_id", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "dotted_order", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "tracingEnabled", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "execution_order", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "child_execution_order", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "attachments", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "replicas", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "distributedParentId", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "_serialized_start_time", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    Object.defineProperty(this, "_awaitInputsOnPost", {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0
    });
    if (isRunTree(originalConfig)) {
      Object.assign(this, { ...originalConfig });
      return;
    }
    const defaultConfig = _RunTree.getDefaultConfig();
    const { metadata, ...config } = originalConfig;
    const client2 = config.client ?? _RunTree.getSharedClient();
    const dedupedMetadata = {
      ...metadata,
      ...config?.extra?.metadata
    };
    config.extra = { ...config.extra, metadata: dedupedMetadata };
    if ("id" in config && config.id == null) {
      delete config.id;
    }
    Object.assign(this, { ...defaultConfig, ...config, client: client2 });
    this.execution_order ??= 1;
    this.child_execution_order ??= 1;
    if (!this.dotted_order) {
      this._serialized_start_time = getMicrosecondPrecisionDatestring(this.start_time, this.execution_order);
    }
    if (!this.id) {
      this.id = uuid7FromTime(this._serialized_start_time ?? this.start_time);
    }
    if (!this.trace_id) {
      if (this.parent_run) {
        this.trace_id = this.parent_run.trace_id ?? this.id;
      } else {
        this.trace_id = this.id;
      }
    }
    this.replicas = _ensureWriteReplicas(this.replicas);
    if (!this.dotted_order) {
      const { dottedOrder } = convertToDottedOrderFormat(this.start_time, this.id, this.execution_order);
      if (this.parent_run) {
        this.dotted_order = this.parent_run.dotted_order + "." + dottedOrder;
      } else {
        this.dotted_order = dottedOrder;
      }
    }
  }
  set metadata(metadata) {
    this.extra = {
      ...this.extra,
      metadata: {
        ...this.extra?.metadata,
        ...metadata
      }
    };
  }
  get metadata() {
    return this.extra?.metadata;
  }
  static getDefaultConfig() {
    const start_time = Date.now();
    return {
      run_type: "chain",
      project_name: getDefaultProjectName(),
      child_runs: [],
      api_url: getEnvironmentVariable("LANGCHAIN_ENDPOINT") ?? "http://localhost:1984",
      api_key: getEnvironmentVariable("LANGCHAIN_API_KEY"),
      caller_options: {},
      start_time,
      serialized: {},
      inputs: {},
      extra: {}
    };
  }
  static getSharedClient() {
    if (!_RunTree.sharedClient) {
      _RunTree.sharedClient = new Client();
    }
    return _RunTree.sharedClient;
  }
  createChild(config) {
    const child_execution_order = this.child_execution_order + 1;
    const inheritedReplicas = this.replicas?.map((replica) => {
      const { reroot, ...rest } = replica;
      return rest;
    });
    const childReplicas = config.replicas ?? inheritedReplicas;
    const child = new _RunTree({
      ...config,
      parent_run: this,
      project_name: this.project_name,
      replicas: childReplicas,
      client: this.client,
      tracingEnabled: this.tracingEnabled,
      execution_order: child_execution_order,
      child_execution_order
    });
    const parentMeta = this.extra?.metadata ?? {};
    const childMeta = child.extra?.metadata ?? {};
    if (Object.keys(parentMeta).length > 0) {
      child.extra = {
        ...child.extra,
        metadata: { ...parentMeta, ...childMeta }
      };
    }
    if (_LC_CONTEXT_VARIABLES_KEY in this) {
      child[_LC_CONTEXT_VARIABLES_KEY] = this[_LC_CONTEXT_VARIABLES_KEY];
    }
    const LC_CHILD = /* @__PURE__ */ Symbol.for("lc:child_config");
    const presentConfig = config.extra?.[LC_CHILD] ?? this.extra[LC_CHILD];
    if (isRunnableConfigLike(presentConfig)) {
      const newConfig = { ...presentConfig };
      const callbacks = isCallbackManagerLike(newConfig.callbacks) ? newConfig.callbacks.copy?.() : void 0;
      if (callbacks) {
        Object.assign(callbacks, { _parentRunId: child.id });
        callbacks.handlers?.find(isLangChainTracerLike)?.updateFromRunTree?.(child);
        newConfig.callbacks = callbacks;
      }
      child.extra[LC_CHILD] = newConfig;
    }
    const visited = /* @__PURE__ */ new Set();
    let current = this;
    while (current != null && !visited.has(current.id)) {
      visited.add(current.id);
      current.child_execution_order = Math.max(current.child_execution_order, child_execution_order);
      current = current.parent_run;
    }
    this.child_runs.push(child);
    return child;
  }
  async end(outputs, error2, endTime = Date.now(), metadata) {
    this.outputs = this.outputs ?? outputs;
    this.error = this.error ?? error2;
    this.end_time = this.end_time ?? endTime;
    if (metadata && Object.keys(metadata).length > 0) {
      this.extra = this.extra ? { ...this.extra, metadata: { ...this.extra.metadata, ...metadata } } : { metadata };
    }
  }
  _convertToCreate(run, runtimeEnv, excludeChildRuns = true) {
    const runExtra = run.extra ?? {};
    if (runExtra?.runtime?.library === void 0) {
      if (!runExtra.runtime) {
        runExtra.runtime = {};
      }
      if (runtimeEnv) {
        for (const [k, v] of Object.entries(runtimeEnv)) {
          if (!runExtra.runtime[k]) {
            runExtra.runtime[k] = v;
          }
        }
      }
    }
    const parent_run_id = run.parent_run?.id ?? run.parent_run_id;
    let child_runs;
    if (!excludeChildRuns) {
      child_runs = run.child_runs.map((child_run) => this._convertToCreate(child_run, runtimeEnv, excludeChildRuns));
    } else {
      child_runs = [];
    }
    return {
      id: run.id,
      name: run.name,
      start_time: run._serialized_start_time ?? run.start_time,
      end_time: run.end_time,
      run_type: run.run_type,
      reference_example_id: run.reference_example_id,
      extra: runExtra,
      serialized: run.serialized,
      error: run.error,
      inputs: run.inputs,
      outputs: run.outputs,
      session_name: run.project_name,
      child_runs,
      parent_run_id,
      trace_id: run.trace_id,
      dotted_order: run.dotted_order,
      tags: run.tags,
      attachments: run.attachments,
      events: run.events
    };
  }
  _sliceParentId(parentId, run) {
    if (run.dotted_order) {
      const segs = run.dotted_order.split(".");
      let startIdx = null;
      for (let idx = 0; idx < segs.length; idx++) {
        const segId = segs[idx].slice(-TIMESTAMP_LENGTH);
        if (segId === parentId) {
          startIdx = idx;
          break;
        }
      }
      if (startIdx !== null) {
        const trimmedSegs = segs.slice(startIdx + 1);
        run.dotted_order = trimmedSegs.join(".");
        if (trimmedSegs.length > 0) {
          run.trace_id = trimmedSegs[0].slice(-TIMESTAMP_LENGTH);
        } else {
          run.trace_id = run.id;
        }
      }
    }
    if (run.parent_run_id === parentId) {
      run.parent_run_id = void 0;
    }
  }
  _setReplicaTraceRoot(replicaKey, traceRootId) {
    const replicaTraceRoots = getContextVar(this, _REPLICA_TRACE_ROOTS_KEY) ?? {};
    replicaTraceRoots[replicaKey] = traceRootId;
    setContextVar(this, _REPLICA_TRACE_ROOTS_KEY, replicaTraceRoots);
    for (const child of this.child_runs) {
      child._setReplicaTraceRoot(replicaKey, traceRootId);
    }
  }
  _remapForProject(params) {
    const { projectName, runtimeEnv, excludeChildRuns = true, reroot = false, distributedParentId, apiUrl, apiKey, workspaceId } = params;
    const baseRun = this._convertToCreate(this, runtimeEnv, excludeChildRuns);
    if (projectName === this.project_name) {
      return {
        ...baseRun,
        session_name: projectName
      };
    }
    if (reroot) {
      if (distributedParentId) {
        this._sliceParentId(distributedParentId, baseRun);
      } else {
        baseRun.parent_run_id = void 0;
        if (baseRun.dotted_order) {
          const segs = baseRun.dotted_order.split(".");
          if (segs.length > 0) {
            baseRun.dotted_order = segs[segs.length - 1];
            baseRun.trace_id = baseRun.id;
          }
        }
      }
      const replicaKey = getReplicaKey({
        projectName,
        apiUrl,
        apiKey,
        workspaceId
      });
      this._setReplicaTraceRoot(replicaKey, baseRun.id);
    }
    let ancestorRerootedTraceId;
    if (!reroot) {
      const replicaTraceRoots = getContextVar(this, _REPLICA_TRACE_ROOTS_KEY) ?? {};
      const replicaKey = getReplicaKey({
        projectName,
        apiUrl,
        apiKey,
        workspaceId
      });
      ancestorRerootedTraceId = replicaTraceRoots[replicaKey];
      if (ancestorRerootedTraceId) {
        baseRun.trace_id = ancestorRerootedTraceId;
        if (baseRun.dotted_order) {
          const segs = baseRun.dotted_order.split(".");
          let rootIdx = null;
          for (let idx = 0; idx < segs.length; idx++) {
            const segId = segs[idx].slice(-TIMESTAMP_LENGTH);
            if (segId === ancestorRerootedTraceId) {
              rootIdx = idx;
              break;
            }
          }
          if (rootIdx !== null) {
            const trimmedSegs = segs.slice(rootIdx);
            baseRun.dotted_order = trimmedSegs.join(".");
          }
        }
      }
    }
    const oldId = baseRun.id;
    const newId = nonCryptographicUuid7Deterministic(oldId, projectName);
    let newTraceId;
    if (baseRun.trace_id) {
      newTraceId = nonCryptographicUuid7Deterministic(baseRun.trace_id, projectName);
    } else {
      newTraceId = newId;
    }
    let newParentId;
    if (baseRun.parent_run_id) {
      newParentId = nonCryptographicUuid7Deterministic(baseRun.parent_run_id, projectName);
    }
    let newDottedOrder;
    if (baseRun.dotted_order) {
      const segs = baseRun.dotted_order.split(".");
      const remappedSegs = segs.map((seg) => {
        const segId = seg.slice(-TIMESTAMP_LENGTH);
        const remappedId = nonCryptographicUuid7Deterministic(segId, projectName);
        return seg.slice(0, -TIMESTAMP_LENGTH) + remappedId;
      });
      newDottedOrder = remappedSegs.join(".");
    }
    return {
      ...baseRun,
      id: newId,
      trace_id: newTraceId,
      parent_run_id: newParentId,
      dotted_order: newDottedOrder,
      session_name: projectName
    };
  }
  async postRun(excludeChildRuns = true) {
    if (this._awaitInputsOnPost) {
      this.inputs = await this.inputs;
    }
    try {
      const runtimeEnv = getRuntimeEnvironment();
      if (this.replicas && this.replicas.length > 0) {
        for (const { projectName, apiKey, apiUrl, workspaceId, reroot } of this.replicas) {
          const runCreate = this._remapForProject({
            projectName: projectName ?? this.project_name,
            runtimeEnv,
            excludeChildRuns: true,
            reroot,
            distributedParentId: this.distributedParentId,
            apiUrl,
            apiKey,
            workspaceId
          });
          await this.client.createRun(runCreate, {
            apiKey,
            apiUrl,
            workspaceId
          });
        }
      } else {
        const runCreate = this._convertToCreate(this, runtimeEnv, excludeChildRuns);
        await this.client.createRun(runCreate);
      }
      if (!excludeChildRuns) {
        warnOnce("Posting with excludeChildRuns=false is deprecated and will be removed in a future version.");
        for (const childRun of this.child_runs) {
          await childRun.postRun(false);
        }
      }
      this.child_runs = [];
    } catch (error2) {
      console.error(`Error in postRun for run ${this.id}:`, error2);
    }
  }
  async patchRun(options) {
    if (this.replicas && this.replicas.length > 0) {
      for (const { projectName, apiKey, apiUrl, workspaceId, updates, reroot } of this.replicas) {
        const runData = this._remapForProject({
          projectName: projectName ?? this.project_name,
          runtimeEnv: void 0,
          excludeChildRuns: true,
          reroot,
          distributedParentId: this.distributedParentId,
          apiUrl,
          apiKey,
          workspaceId
        });
        const updatePayload = {
          id: runData.id,
          name: runData.name,
          run_type: runData.run_type,
          start_time: runData.start_time,
          outputs: runData.outputs,
          error: runData.error,
          parent_run_id: runData.parent_run_id,
          session_name: runData.session_name,
          reference_example_id: runData.reference_example_id,
          end_time: runData.end_time,
          dotted_order: runData.dotted_order,
          trace_id: runData.trace_id,
          events: runData.events,
          tags: runData.tags,
          extra: runData.extra,
          attachments: this.attachments,
          ...updates
        };
        if (!options?.excludeInputs) {
          updatePayload.inputs = runData.inputs;
        }
        await this.client.updateRun(runData.id, updatePayload, {
          apiKey,
          apiUrl,
          workspaceId
        });
      }
    } else {
      try {
        const runUpdate = {
          name: this.name,
          run_type: this.run_type,
          start_time: this._serialized_start_time ?? this.start_time,
          end_time: this.end_time,
          error: this.error,
          outputs: this.outputs,
          parent_run_id: this.parent_run?.id ?? this.parent_run_id,
          reference_example_id: this.reference_example_id,
          extra: this.extra,
          events: this.events,
          dotted_order: this.dotted_order,
          trace_id: this.trace_id,
          tags: this.tags,
          attachments: this.attachments,
          session_name: this.project_name
        };
        if (!options?.excludeInputs) {
          runUpdate.inputs = this.inputs;
        }
        await this.client.updateRun(this.id, runUpdate);
      } catch (error2) {
        console.error(`Error in patchRun for run ${this.id}`, error2);
      }
    }
    this.child_runs = [];
  }
  toJSON() {
    return this._convertToCreate(this, void 0, false);
  }
  /**
   * Add an event to the run tree.
   * @param event - A single event or string to add
   */
  addEvent(event) {
    if (!this.events) {
      this.events = [];
    }
    if (typeof event === "string") {
      this.events.push({
        name: "event",
        time: (/* @__PURE__ */ new Date()).toISOString(),
        message: event
      });
    } else {
      this.events.push({
        ...event,
        time: event.time ?? (/* @__PURE__ */ new Date()).toISOString()
      });
    }
  }
  static fromRunnableConfig(parentConfig, props) {
    const callbackManager = parentConfig?.callbacks;
    let parentRun;
    let projectName;
    let client2;
    let tracingEnabled = isTracingEnabled();
    if (callbackManager) {
      const parentRunId = callbackManager?.getParentRunId?.() ?? "";
      const langChainTracer = callbackManager?.handlers?.find((handler) => handler?.name == "langchain_tracer");
      parentRun = langChainTracer?.getRun?.(parentRunId);
      projectName = langChainTracer?.projectName;
      client2 = langChainTracer?.client;
      tracingEnabled = tracingEnabled || !!langChainTracer;
    }
    if (!parentRun) {
      return new _RunTree({
        ...props,
        client: client2,
        tracingEnabled,
        project_name: projectName
      });
    }
    const parentRunTree = new _RunTree({
      name: parentRun.name,
      id: parentRun.id,
      trace_id: parentRun.trace_id,
      dotted_order: parentRun.dotted_order,
      client: client2,
      tracingEnabled,
      project_name: projectName,
      tags: [
        ...new Set((parentRun?.tags ?? []).concat(parentConfig?.tags ?? []))
      ],
      extra: {
        metadata: {
          ...parentRun?.extra?.metadata,
          ...parentConfig?.metadata
        }
      }
    });
    return parentRunTree.createChild(props);
  }
  static fromDottedOrder(dottedOrder) {
    return this.fromHeaders({ "langsmith-trace": dottedOrder });
  }
  static fromHeaders(headers, inheritArgs) {
    const rawHeaders = "get" in headers && typeof headers.get === "function" ? {
      "langsmith-trace": headers.get("langsmith-trace"),
      baggage: headers.get("baggage")
    } : headers;
    const headerTrace = rawHeaders["langsmith-trace"];
    if (!headerTrace || typeof headerTrace !== "string")
      return void 0;
    const parentDottedOrder = headerTrace.trim();
    const parsedDottedOrder = parentDottedOrder.split(".").map((part) => {
      const [strTime, uuid] = part.split("Z");
      return { strTime, time: Date.parse(strTime + "Z"), uuid };
    });
    const traceId = parsedDottedOrder[0].uuid;
    const config = {
      ...inheritArgs,
      name: inheritArgs?.["name"] ?? "parent",
      run_type: inheritArgs?.["run_type"] ?? "chain",
      start_time: inheritArgs?.["start_time"] ?? Date.now(),
      id: parsedDottedOrder.at(-1)?.uuid,
      trace_id: traceId,
      dotted_order: parentDottedOrder
    };
    if (rawHeaders["baggage"] && typeof rawHeaders["baggage"] === "string") {
      const baggage = Baggage.fromHeader(rawHeaders["baggage"]);
      config.metadata = baggage.metadata;
      config.tags = baggage.tags;
      config.project_name = baggage.project_name;
      config.replicas = baggage.replicas;
    }
    const runTree = new _RunTree(config);
    runTree.distributedParentId = runTree.id;
    return runTree;
  }
  toHeaders(headers) {
    const result = {
      "langsmith-trace": this.dotted_order,
      baggage: new Baggage(this.extra?.metadata, this.tags, this.project_name, this.replicas).toHeader()
    };
    if (headers) {
      for (const [key, value] of Object.entries(result)) {
        headers.set(key, value);
      }
    }
    return result;
  }
};
Object.defineProperty(RunTree, "sharedClient", {
  enumerable: true,
  configurable: true,
  writable: true,
  value: null
});
function isRunTree(x) {
  return x != null && typeof x.createChild === "function" && typeof x.postRun === "function";
}
function isLangChainTracerLike(x) {
  return typeof x === "object" && x != null && typeof x.name === "string" && x.name === "langchain_tracer";
}
function containsLangChainTracerLike(x) {
  return Array.isArray(x) && x.some((callback) => isLangChainTracerLike(callback));
}
function isCallbackManagerLike(x) {
  return typeof x === "object" && x != null && Array.isArray(x.handlers);
}
function isRunnableConfigLike(x) {
  const callbacks = x?.callbacks;
  return x != null && typeof callbacks === "object" && // Callback manager with a langchain tracer
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (containsLangChainTracerLike(callbacks?.handlers) || // Or it's an array with a LangChainTracerLike object within it
  containsLangChainTracerLike(callbacks));
}
function _getWriteReplicasFromEnv() {
  const envVar = getEnvironmentVariable("LANGSMITH_RUNS_ENDPOINTS");
  if (!envVar)
    return [];
  try {
    const parsed = JSON.parse(envVar);
    if (Array.isArray(parsed)) {
      const replicas2 = [];
      for (const item of parsed) {
        if (typeof item !== "object" || item === null) {
          console.warn(`Invalid item type in LANGSMITH_RUNS_ENDPOINTS: expected object, got ${typeof item}`);
          continue;
        }
        if (typeof item.api_url !== "string") {
          console.warn(`Invalid api_url type in LANGSMITH_RUNS_ENDPOINTS: expected string, got ${typeof item.api_url}`);
          continue;
        }
        if (typeof item.api_key !== "string") {
          console.warn(`Invalid api_key type in LANGSMITH_RUNS_ENDPOINTS: expected string, got ${typeof item.api_key}`);
          continue;
        }
        replicas2.push({
          apiUrl: item.api_url.replace(/\/$/, ""),
          apiKey: item.api_key
        });
      }
      return replicas2;
    } else if (typeof parsed === "object" && parsed !== null) {
      _checkEndpointEnvUnset(parsed);
      const replicas2 = [];
      for (const [url, key] of Object.entries(parsed)) {
        const cleanUrl = url.replace(/\/$/, "");
        if (typeof key === "string") {
          replicas2.push({
            apiUrl: cleanUrl,
            apiKey: key
          });
        } else {
          console.warn(`Invalid value type in LANGSMITH_RUNS_ENDPOINTS for URL ${url}: expected string, got ${typeof key}`);
          continue;
        }
      }
      return replicas2;
    } else {
      console.warn(`Invalid LANGSMITH_RUNS_ENDPOINTS \u2013 must be valid JSON array of objects with api_url and api_key properties, or object mapping url->apiKey, got ${typeof parsed}`);
      return [];
    }
  } catch (e) {
    if (isConflictingEndpointsError(e)) {
      throw e;
    }
    console.warn("Invalid LANGSMITH_RUNS_ENDPOINTS \u2013 must be valid JSON array of objects with api_url and api_key properties, or object mapping url->apiKey");
    return [];
  }
}
function _ensureWriteReplicas(replicas2) {
  if (replicas2) {
    return replicas2.map((replica) => {
      if (Array.isArray(replica)) {
        return {
          projectName: replica[0],
          updates: replica[1]
        };
      }
      return replica;
    });
  }
  return _getWriteReplicasFromEnv();
}
function _checkEndpointEnvUnset(parsed) {
  if (Object.keys(parsed).length > 0 && getLangSmithEnvironmentVariable("ENDPOINT")) {
    throw new ConflictingEndpointsError();
  }
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/uuid.js
function uuid7() {
  return v7_default();
}

// node_modules/.pnpm/langsmith@0.5.18/node_modules/langsmith/dist/index.js
var __version__ = "0.5.18";

// dist/logger.js
import { appendFileSync, mkdirSync as mkdirSync3, statSync, renameSync as renameSync3 } from "node:fs";
import { dirname } from "node:path";
var MAX_LOG_BYTES = 5 * 1024 * 1024;
var LOG_FILE = process.env.CC_LANGSMITH_LOG_FILE ?? `${process.env.HOME ?? ""}/.claude/state/hook.log`;
var debugEnabled = false;
function initLogger(debug2) {
  debugEnabled = debug2;
  mkdirSync3(dirname(LOG_FILE), { recursive: true });
}
function rotateIfNeeded() {
  try {
    if (statSync(LOG_FILE).size >= MAX_LOG_BYTES) {
      renameSync3(LOG_FILE, `${LOG_FILE}.1`);
    }
  } catch {
  }
}
function write(level, message) {
  const timestamp = (/* @__PURE__ */ new Date()).toISOString().replace("T", " ").replace("Z", "");
  const line = `${timestamp} [${level}] ${message}
`;
  try {
    rotateIfNeeded();
    appendFileSync(LOG_FILE, line);
  } catch {
  }
}
function error(message) {
  write("ERROR", message);
}
function debug(message) {
  if (debugEnabled) {
    write("DEBUG", message);
  }
}

// dist/transcript.js
import { readFileSync as readFileSync3, statSync as statSync2, openSync, readSync, closeSync } from "node:fs";
var MAX_FULL_READ_BYTES = 50 * 1024 * 1024;

// dist/state.js
import { readFileSync as readFileSync4, writeFileSync as writeFileSync3, mkdirSync as mkdirSync4, openSync as openSync2, closeSync as closeSync2, unlinkSync as unlinkSync3 } from "node:fs";
import { dirname as dirname2 } from "node:path";
var LOCK_TIMEOUT_MS = 5e3;
var LOCK_RETRY_MS = 20;
function lockPath(stateFilePath) {
  return `${stateFilePath}.lock`;
}
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
async function acquireLock(stateFilePath) {
  const lock = lockPath(stateFilePath);
  const deadline = Date.now() + LOCK_TIMEOUT_MS;
  mkdirSync4(dirname2(stateFilePath), { recursive: true });
  while (Date.now() < deadline) {
    try {
      const fd = openSync2(lock, "wx");
      closeSync2(fd);
      return;
    } catch {
      await sleep(LOCK_RETRY_MS);
    }
  }
  try {
    unlinkSync3(lock);
  } catch {
  }
}
function releaseLock(stateFilePath) {
  try {
    unlinkSync3(lockPath(stateFilePath));
  } catch {
  }
}
async function atomicUpdateState(stateFilePath, fn) {
  await acquireLock(stateFilePath);
  try {
    const state = loadState(stateFilePath);
    writeFileSync3(stateFilePath, JSON.stringify(fn(state), null, 2));
  } finally {
    releaseLock(stateFilePath);
  }
}
function loadState(stateFilePath) {
  try {
    const raw = readFileSync4(stateFilePath, "utf-8");
    return JSON.parse(raw);
  } catch {
    return {};
  }
}
function getSessionState(state, sessionId) {
  return state[sessionId] ?? {
    last_line: -1,
    turn_count: 0,
    updated: "",
    task_run_map: {}
  };
}
var SESSION_MAX_AGE_MS = 24 * 60 * 60 * 1e3;

// dist/langsmith.js
var client = void 0;
var replicas = void 0;
function initTracing(apiKey, apiUrl, providedReplicas) {
  if (apiKey) {
    client = new Client({ apiKey, apiUrl });
  } else {
    client = void 0;
  }
  replicas = providedReplicas;
  return client;
}
async function flushPendingTraces() {
  debug("Awaiting pending trace batches...");
  await Promise.all([
    client?.awaitPendingTraceBatches(),
    RunTree.getSharedClient().awaitPendingTraceBatches()
  ]);
  debug("Trace batches flushed successfully");
}
function generateDottedOrderSegment(time, runId) {
  const iso = typeof time === "string" ? time : new Date(time).toISOString();
  const isoWithMicroseconds = `${iso.slice(0, -1)}000Z`;
  const stripped = isoWithMicroseconds.replace(/[-:.]/g, "");
  return stripped + runId;
}

// dist/config.js
function loadConfig() {
  const apiKey = process.env.CC_LANGSMITH_API_KEY ?? process.env.LANGSMITH_API_KEY ?? "";
  const project = process.env.CC_LANGSMITH_PROJECT ?? "claude-code";
  const apiBaseUrl = process.env.LANGSMITH_ENDPOINT ?? "https://api.smith.langchain.com";
  const homeDir = process.env.HOME ?? process.env.USERPROFILE ?? "";
  const stateFilePath = process.env.STATE_FILE ?? `${homeDir}/.claude/state/langsmith_state.json`;
  const debug2 = (process.env.CC_LANGSMITH_DEBUG ?? "").toLowerCase() === "true";
  let replicas2;
  const providedReplicas = process.env.CC_LANGSMITH_RUNS_ENDPOINTS;
  if (providedReplicas !== void 0) {
    try {
      replicas2 = JSON.parse(providedReplicas);
    } catch {
      error("Failed to parse provided CC_LANGSMITH_RUNS_ENDPOINTS. Please make sure they are valid JSON.");
    }
  }
  const parentDottedOrder = process.env.CC_LANGSMITH_PARENT_DOTTED_ORDER || void 0;
  let customMetadata;
  const providedMetadata = process.env.CC_LANGSMITH_METADATA;
  if (providedMetadata !== void 0) {
    try {
      const parsed = JSON.parse(providedMetadata);
      if (typeof parsed === "object" && parsed !== null && !Array.isArray(parsed)) {
        customMetadata = parsed;
      } else {
        error("CC_LANGSMITH_METADATA must be a JSON object (not an array or primitive).");
      }
    } catch {
      error("Failed to parse provided CC_LANGSMITH_METADATA. Please make sure it is valid JSON.");
    }
  }
  return {
    apiKey,
    project,
    apiBaseUrl,
    stateFilePath,
    debug: debug2,
    parentDottedOrder,
    replicas: replicas2,
    customMetadata
  };
}

// dist/utils/hook-init.js
function initHook() {
  const config = loadConfig();
  initLogger(config.debug);
  if (process.env.TRACE_TO_LANGSMITH?.toLowerCase() !== "true") {
    return null;
  }
  if (!config.apiKey && (!config.replicas || config.replicas.length === 0)) {
    error("No API key set (CC_LANGSMITH_API_KEY or LANGSMITH_API_KEY) and no replicas configured");
    return null;
  }
  return config;
}

// dist/utils/stdin.js
function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => data += chunk);
    process.stdin.on("end", () => {
      try {
        resolve(JSON.parse(data));
      } catch (err) {
        reject(new Error(`Failed to parse hook input: ${err}`));
      }
    });
    process.stdin.on("error", reject);
  });
}

// dist/hooks/post-tool-use.js
async function main() {
  const input = await readStdin();
  const config = initHook();
  if (!config)
    return;
  if (input.agent_id || input.agent_type) {
    debug("Skipping PostToolUse for subagent tool \u2014 Stop hook handles tracing");
    return;
  }
  const client2 = initTracing(config.apiKey, config.apiBaseUrl, config.replicas);
  const state = loadState(config.stateFilePath);
  const sessionState = getSessionState(state, input.session_id);
  const parentRunId = sessionState.current_turn_run_id;
  const traceId = sessionState.current_trace_id;
  const parentDottedOrder = sessionState.current_dotted_order;
  if (!parentRunId || !traceId || !parentDottedOrder) {
    error("No current_turn_run_id or trace_id in state - UserPromptSubmit hook may not have run");
    return;
  }
  const toolRunId = uuid7();
  const startTime = sessionState.tool_start_times?.[input.tool_use_id] ?? Date.now();
  const toolEndTime = Date.now();
  const startTimeIso = new Date(startTime).toISOString();
  const toolEndTimeIso = new Date(toolEndTime).toISOString();
  const toolDottedOrderSegment = generateDottedOrderSegment(startTime, toolRunId);
  const toolDottedOrder = `${parentDottedOrder}.${toolDottedOrderSegment}`;
  const agentId = input.tool_response.agentId;
  if (agentId) {
    debug(`Agent tool detected, deferring run creation for ${agentId} -> ${toolRunId}`);
  } else {
    const runTree = new RunTree({
      client: client2,
      replicas: config.replicas,
      id: toolRunId,
      name: input.tool_name,
      run_type: "tool",
      inputs: { input: input.tool_input },
      outputs: { output: input.tool_response },
      project_name: config.project,
      start_time: startTimeIso,
      end_time: toolEndTimeIso,
      parent_run_id: parentRunId,
      trace_id: traceId,
      dotted_order: toolDottedOrder,
      extra: {
        metadata: {
          thread_id: input.session_id,
          ls_integration: "claude-code",
          tool_name: input.tool_name,
          ...config.customMetadata
        }
      }
    });
    await runTree.postRun();
  }
  await atomicUpdateState(config.stateFilePath, (freshState) => {
    const freshSession = getSessionState(freshState, input.session_id);
    return {
      ...freshState,
      [input.session_id]: {
        ...freshSession,
        last_tool_end_time: toolEndTime,
        ...agentId ? {
          task_run_map: {
            ...freshSession.task_run_map,
            [agentId]: {
              run_id: toolRunId,
              dotted_order: toolDottedOrder,
              deferred: {
                trace_id: traceId,
                parent_run_id: parentRunId,
                start_time: startTimeIso,
                end_time: toolEndTimeIso,
                inputs: input.tool_input,
                outputs: input.tool_response,
                project_name: config.project
              }
            }
          }
        } : {
          // Record tool_use_id so traceTurn skips it (avoids double-tracing).
          traced_tool_use_ids: [...freshSession.traced_tool_use_ids ?? [], input.tool_use_id]
        }
      }
    };
  });
  if (!agentId) {
    await flushPendingTraces();
  }
}
main().catch((err) => {
  try {
    error(`PostToolUse hook fatal error: ${err}`);
  } catch {
  }
  process.exit(0);
});
