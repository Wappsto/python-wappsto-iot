v0.5.6 (Jan 31 2022)
===============================================================================

## Added
 * Ping-pong option in the config-method.
 * fast_send option in the config-method.

## Fixed

 * Fix some issues that only happen on first time run.
 * Fix a issue where config was not called, the config-folder was not set to current folder.
 * Fix a issue where offline storage, did not allow the program to stop, if there was still data to be send.
 * Fix a issue with the way the certificates was created, it was not possible to share the network with someone.


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
