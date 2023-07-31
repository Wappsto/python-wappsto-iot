Python Wappsto IoT
===============================================================================


Python Wappsto IoT - Structure
-------------------------------------------------------------------------------

```
                    +---------------+
                    |               |   * Simplify Interface
                    |  Abstraction  |   * Name To UUID Mapping
                    |               |
                    +---------------+
                    |               |   * Callback Handling
                    |    Service    |   * Save/load
                    |               |   * UUID Mapping
                    +---------------+
                    |               |   * JSON Schema
                    |    Protocol   |   * RPC-Protocol
                    |               |
                    +---------------+
                    |               |
                    |   Connection  |   * SSL/TLS Socket
                    |               |
                    +---------------+
```

---

Python Wappsto IoT Threading Structure Ideas.
-------------------------------------------------------------------------------

 1)
    The Protocol & Connection runs in one thread, to ensure that there can be
    prioritized the order of when & that to be send. (Look into 'select')

 2) On receive of data, if there is registered a callback, it should be passed on
    to a thread-pool, so it will not hold the process.

 3) On delivery of data it should, from the user side, be added to a queue,
    but still be waiting on the reply from the server, on that it have received
    the data. If it have not received the date it should raise a exception.

 \*) All callback creates a new thread to be executed in (or Threadpool),
    unless the given callback are running. If it is, drop the given try.

---

Local Storage
-------------------------------------------------------------------------------

The Certificates needed: ´ca.crt´,´client.crt´ & ´client.key´

---

Wappsto IoT - Expectations Alignment
-------------------------------------------------------------------------------


**Information Flow:**

OnChange == PUT                  - Control
OnRequest == POST, GET & DELETE  + Control


|   IoT API              | Flow |        Rest API         |
|    ----                | ---- |          ------         |
| .onChange              |  <-  |  .change                |
|                        |      |                         |
| .onRequest             |      |  .request               |
| - Device.onRequest     |  <-  |  - Device.createValue   |
| - Network.onRequest    |  <-  |  - Network.createDevice |
| - Value.onControl      |  <-  |  - Value.control        |
| - .onRefresh           |  <-  |  - .refresh             |
| - .onDelete            |  <-  |  - .delete              |
|                        |      |                         |
| Device.createValue     |  ->  |    Device.onChange      |
| Network.createDevice   |  ->  |    Network.onChange     |
| .change                |  ->  |    .onChange            |
| - Value.Report         |  ->  |    Value.onReport       |
|                        |      |                         |

 * A 'change' should also be able to trigger a 'report'.
 * onChange Should be able to 'listen' for a specific parameter change.

---

**When a Unit receives:**

| Method | Service |                     Meanings                   |         IoT-API          |
|  ----  |  ----   |                       ----                     |           ---            |
| POST   | NETWORK | This behavior is not possible.                 |                          |
| GET    | NETWORK | No defined behavior.                           | WappstoIoT.onChange      |
|        |         |                                                | WappstoIoT.onRefresh     |
| PUT    | NETWORK | Change the Network Name/Description            | WappstoIoT.onRequest     |
| DELETE | NETWORK | Used to soft reset the unit, with a following  | WappstoIoT.onChange      |
|        |         | recreation of the entire model.                | WappstoIoT.onDelete      |
|        |
| POST   | DEVICE  | Request a creation of Device. Can be refused.  | WappstoIoT.onRequest     |
|        |         |                                                | device.onRequest         |
|        |         |                                                | value.onRequest          |
| GET    | DEVICE  | No defined behavior.                           | device.onRequest         |
|        |         |                                                | device.onRefresh         |
| PUT    | DEVICE  | Change a parameter (like Version/Manufacture)  | device.onChange          |
| DELETE | DEVICE  | Used to remove a Device. (Informational)       | device.onRequest         |
|        |         |                                                | device.onDelete          |
|        |
| POST   | VALUE   | Request a creation of Value. Can be refused.   | device.onRequest         |
|        |         |                                                | value.onChange           |
| GET    | VALUE   | Used to trigger a report state refresh.        | value.onRequest          |
|        |         |                                                | value.onRefresh          |
| PUT    | VALUE   | Change a parameter (like Delta/period)         | value.onChange           |
| DELETE | VALUE   | Used to remove a Value. (Informational)        | value.onRequest          |
|        |         |                                                | value.onDelete           |
|        |
| POST   | STATE   | Request a creation of State. Can be refused.   | value.onRequest          |
|        |         |                                                | state.onRequest          |
| GET    | STATE   | Used to trigger a refresh                      | value.onRequest          |
|        |         |                                                | value.onRefresh          |
|        |         |                                                | state.onRequest          |
|        |         |                                                | state.onRefresh
| PUT    | STATE   | (Control) Used to change a state               | (control)value.onRequest |
|        |         |                                                | (control)value.onControl |
|        |         |                                                | state.onRequest
| PUT    | STATE   | (Report) Error, can not control a report.      |                          |
| DELETE | STATE   | Used to remove a State. (Informational)        | value.onRequest          |
|        |         |                                                | state.onDelete

**When a Unit sends:**

|         IoT-API          |                     Meanings                   | Method | Service |
|           ---            |                       ----                     |  ----  |  ----   |
| WappstoIoT.connect       | Creation of Network.                           | POST   | NETWORK |
| (WappstoIoT.config)      |                                                | GET    | NETWORK |
| WappstoIoT.change        |                                                | PUT    | NETWORK |
| WappstoIoT.delete        | Used to unclaim a Network & delete all children| DELETE | NETWORK |
|                          |
| WappstoIoT.createDevice  | Creation of Device.                            | POST   | DEVICE  |
| (WappstoIoT.config)      |                                                | GET    | DEVICE  |
| device.change            |                                                | PUT    | DEVICE  |
| device.delete            | Used to remove a Device, & all children.       | DELETE | DEVICE  |
|                          |
| device.createValue       | Creation of Value.                             | POST   | VALUE   |
| (WappstoIoT.config)      |                                                | GET    | VALUE   |
| value.change             |                                                | PUT    | VALUE   |
| value.delete             | Used to remove a Value, & all children.        | DELETE | VALUE   |
|                          |
| device.createValue       | Creation of State.                             | POST   | STATE   |
| (WappstoIoT.config)      |                                                | GET    | STATE   |
| value.report  (Report)   |                                                | PUT    | STATE   |
| value.change  (Report)   |                                                |        |         |
| state.control (Control)  |                                                |        |         |
| value.request (Control)  |                                                |        |         |
| value.change (Permission)| Used to remove a State.                        | DELETE | STATE   |
| state.delete             |                                                |        |         |
---


**Updates behind the Screen:**

---
Control data should be the only value, that are updated & save by the Library.


**Trace:**

---

The Trace Should, if possible, be tracing through the program.
Which means that, a given reply (if any) to a request, should be traced as a
child of that request, even duo it is through the user code.

A way of setting this up, will be to alway give a object to the callback, that
is the object that have been changed, but also the object that should be used
to send a reply, if any, back to the server. That Object should ba a "Shadow"
object of the existing object, with the only change that, it enforces a trace,
on whatever are send from it, that are a child from the request.


NOTEs:
===============================================================================
 * Bulk send data.
 * Send Blob data with encoding.
 * Send data with old timestamp.

 * Need to refresh the control value after a sleep.

Future Ideas:
 * POST Device: Setup a new HW Device. (need a HWsetting, maybe in the name?)


Known Bugs {icon bug color=red}
===============================================================================
* [ ] Sometimes Wappsto do not reply on a 'lookup' request, so a duplicate is make.


Unsure {icon question-circle color=blue}
===============================================================================
* [ ] What should be send back on a JsonRpc Success, with trace?
* [ ] How should a trace through the system, (->control->reply) be handled?


TODO List {icon cog spin}
===============================================================================
* [x] Batch the packages.
* [ ] Make a test to ensure that the timezones are right.
* [ ] Documentation.
* [ ] System Test.
* [ ] If connection issue doing creation, reconnect or raise Error.
* [x] Autogen code Stub with: [Tool](https://mypy.readthedocs.io/en/stable/stubgen.html)
* [ ] Make a github-test for Python v3.6.7
* [ ] Detect if multiple is using same Certificate. (it disconnects Multiple times if it is the case)
* [ ] [Pydantic Migrate to v2](https://docs.pydantic.dev/2.0/migration/)
* [ ] Enable `value.report` to take `LogValues` and/or `list[LogValues]`.