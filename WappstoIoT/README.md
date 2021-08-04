Wappsto IoT
===============================================================================


Wappsto IoT - Structure
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


Notes
-------------------------------------------------------------------------------
In the setuptools setup there is a optional dependencies (only) input:
```bash
pip3 install pyWappsto[extended]
```



Known Bugs {icon bug color=red}
===============================================================================



Unsure {icon question-circle color=blue}
===============================================================================
* [ ] Still Everything!!!!


TODO List {icon cog spin}
===============================================================================
* [ ] Writing the System.
* [ ] Documentation.
* [ ] System Test.
