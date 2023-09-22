v0.7.0 (Sep 22 2023)
===============================================================================

## Changed
 * Breaking Change! - If the server do not reply on any messages, it will now cast a `TimeoutError` exception.


v0.6.10 (Sep 15 2023)
===============================================================================
## Added
 * `remove_illegal_characters` function to help remove the illegal characters.

## Changed
 * Extended the legal characters list for name.


v0.6.9 (Aug 18 2023)
===============================================================================
## Removed
 * The CLI interface to create certificates. Use `https://wappsto.com/store/application/iot_certificate_manager` instead.
 * Remove the `Tracer` (Package flow tracing).

## Changed
 * Pydantic version to be between 1.0.0 & 2.0.0 for better compatibility.


v0.6.8 (Aug 04 2023)
===============================================================================
## Added
 * `report` now take a `LogValue` or a list of `LogValue`s.

## Changed
 * It will now bulk report data, if a list af `LogValue`s is given.
 * Bulk report data will now be sorted.

## Fixed
 * Handle a rare error case from the server.


v0.6.7 (Jul 07 2023)
===============================================================================
## Added
 * Scandinavian special letters to the legal list

## Changed
 * Updated the `wappstoiot.ValueTemplate` to version v0.0.5
 * Set Pydantic version to be `v1.10.11` until migration to `v2` is done.

v0.6.6 (Jun 22 2023)
===============================================================================
## Added
 * Code Stub.

## Changed
 * Now inform which characters are illegal in the given name.

## Fixed
 * The `getReportTimestamp` & `getControlTimestamp` now ensures the return is `None` or of type datetime.

v0.6.5 (Feb 28 2023)
===============================================================================
## Fixed
 * Report & Control now generate a timestamp in UTC time.

v0.6.4 (Feb 27 2023)
===============================================================================

## Added
 * onControlCancel
 * onReportCancel

## Fixed
 * Check on the argument count on callbacks on adding them.
 * Now the on-function returns the callback it was given.
 * Should now covert the timestamp correctly.
 * Fix an issue where it could not close the socket.

## Changed
 * Updated the `wappstoiot.ValueTemplate` to version 0.0.3

v0.6.3 (May 5 2022)
===============================================================================

## Fixed
 * Fixed a issue with the control method, there it broke if it got out of sink with the report.
 * `getReportData` now returns the Report data instead of control.
 * Fixed a issue that prevented in report/control values with old timestamps.

v0.6.2 (Mar 10 2022)
===============================================================================

## Fixed
 * Now `pathlib.Path` can also be used for the config config_folder input.
 * Fixed a issue where it always where asking for the value.
 * Fixed a issue where it did not create the need states, if the device existed. 
 * Fixed a issue where it will fail om the smallest schema change.

## Changed

 * Naming policy are now enforced. Have to be set, and may only contain:
    ALPHA/DIGIT/" . "/" ~ "/"(space)"/" - "/" _ "
 * Breaking Change! - Changes the 'ValueTypes' to 'ValueTemplates', which are a more meaningful name. The createValue input 'value_type', have also change to 'value_template'
 * Enforce the parameter-name for multiple inputs in the create-methods. 


v0.6.1 (Feb 21 2022)
===============================================================================

## Changed

 * Updated the ValueTypes to use the Default template values v0.0.1.


v0.6.0 (Jan 31 2022)
===============================================================================

## Added
 * Ping-pong option in the config-method.
 * fast_send option in the config-method.

## Fixed

 * Fix some issues that only happen on first time run.
 * Fix a issue where if config was not called, the config-folder was not set to current folder.
 * Fix a issue where offline storage, did not allow the program to stop, if there was still data to be send.
 * Fix a issue with the way the certificates was created the right way, and is also claimed.


v0.5.5 (Dec 21 2021)
===============================================================================

## Fixed

 * Fix a issue that prevented wappstoiot in creating a new value.


v0.5.4 (Dec 21 2021)
===============================================================================

## Added

 * New Default Value-Types. (CO2, Humidity & Pressure Pascal).


## Changed

 * The createValue, are now split into 5. `createValue` that uses the predefined ValueType given, and 1 for each base value types, for when a custom is needed. 
 * `permission` is now required.
 * `onControl`, `onReport`, `getControlData` & `getReportData` provides a float if the value was set to be a number.


## Fixed

 * offline_Storage warnings now fixed.
 * A issue where the `type`-value inside value where not set.
 * A issue where the step was set to a int, not a float.
 * `wappstoiot.onStatus` should not be working correctly.


v0.5.3 (Dec 9, 2021)
===============================================================================

## Added

 * Groove Examples for Raspberry Pi.
 * Checks of naming, so it reuses the object based on the name. (Naming are mandatory now.)
 * `wappstoiot.config` have been added to handle all the configs.
 * `wappstoiot.createNetwork` have been added to streamline the flow.
 * `value.getReportTimestamp()`, `value.getControlTimestamp()` have been added to make the timestamp for the last given value accessible.
 * `value.getControlData()` have been added to make the control data accessible.

## Removed

 * Remove the Module ids. (The Names are now the unique identifier.)
 * Remove `Rich` dependency.

## Changed

 * The names & naming convention to fix the other Wappsto Libraries.
 * All the connections & general configs are moved from the Network, to wappstoiot.
 * `value.data` have been changed to `value.getReportData()`

## Fixed

 * Fix the naming to fit the naming convention.


v0.5.2 (Nov 25, 2021)
===============================================================================

## Added

 * HTTP Proxy support. (Pulls #259, #353)

## Fixed

 * Make WappstoIoT python3.6 compatible.
 * Fix a Path issue that make the code not able to find the certificates in ipython.


v0.5.1 (Nov 23, 2021)
===============================================================================

## Added

 * Pip release.

## Fixed

 * Fix the name to fit the naming convention.


v0.5.0 (September 20, 2021)
===============================================================================

## Added

 * First Release.
