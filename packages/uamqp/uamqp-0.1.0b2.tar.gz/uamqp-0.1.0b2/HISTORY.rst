.. :changelog:

Release History
===============

0.1.0b2 (2018-04-06)
++++++++++++++++++++

- Added message send retry.
- Added timeouts and better error handling for management requests.
- Improved connection and auth error handling and error messages.
- Fixed message annotations type.
- SendClient.send_all_messages() now returns a list of message send statuses.
- Fixed OpenSSL platform being initialized multiple times.
- Fixed auto-refresh of SAS tokens.
- Altered `receive_batch` behaviour to return messages as soon as they're available.
- Parameter `batch_size` in `receive_batch` renamed to `max_batch_size`.
- Fixed message `application_properties` decode error.
- Removed MacOS dependency on OpenSSL and libuuid.


0.1.0b1 (2018-03-24)
++++++++++++++++++++

- Added management request support.
- Fixed message-less C operation ValueError.
- Store message metadata in Python rather than C.
- Refactored Send and Receive clients to create a generic parent AMQPClient.
- Fixed None receive timestamp bug.
- Removed async iterator queue due to instabilities - all callbacks are now synchronous.


0.1.0a3 (2018-03-19)
++++++++++++++++++++

- Added support for asynchronous message receive by iterator or batch.
- Removed synchronous receive iterator, and replaced with synchronous batch receive.
- Added sync and async context managers for Send and Receive Clients.
- Fixed token instability and added put token retry policy.
- Exposed Link ATTACH properties.
- A connection now has a single $cbs session that can be reused between clients.
- Added C debug trace logging to the Python logger ('uamqp.c_uamqp')


0.1.0a2 (2018-03-12)
++++++++++++++++++++

- Exposed OPEN performative properties for connection telemetry.
- Exposed setters for message.message_annotations and message.application_properties.
- Made adjustments to connection open and close to facilitate sharing a connection object between send/receive clients.
- Support for username/password embedded in connection URI.
- Clients can now optionally leave connection/session/link open for re-use.
- Updated build process and installation instructions.
- Various bug fixes to increase stability.


0.1.0a1 (2018-03-04)
++++++++++++++++++++

- Initial release