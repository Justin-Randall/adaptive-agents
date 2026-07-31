# Event Delivery Diagnostics

Use this playbook when debugging unreliable multi-client event delivery (server-sent events, WebSockets, notifications, in-process pub/sub) where updates appear to reach some clients but not others.

## Check the concurrency primitive first

Before tuning producer timing, debounce behavior, or transport mechanics, compare the delivery semantics of the concurrency primitive with the system contract:

- A **shared destructive queue** models competing workers — each event is removed by exactly one consumer.
- A **broadcast** delivers every event to every subscriber, typically implemented as one queue per subscriber.

If the contract says "every client receives every event" but the primitive is a shared queue, the failure is semantic, not a timing or transport defect. Nondeterministic "sometimes it updates" behavior is the signature of work distribution being mistaken for broadcast.

## Verify with two concurrent consumers

A single-client test cannot distinguish work-queue delivery from broadcast. When multi-subscriber delivery matters:

1. Connect at least two consumers concurrently.
2. Publish one event.
3. Confirm every connected consumer receives it.

If only one consumer receives the event, the primitive is competing-consumer, not broadcast.

## Key heuristic

- Debug the delivery semantics first; tune timing and add polling only after the primitive provably matches the contract.
- Use at least two concurrent consumers whenever the contract requires broadcast.
