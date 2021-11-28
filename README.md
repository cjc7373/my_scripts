Talk is cheap, show me the code.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC2119](https://www.rfc-editor.org/rfc/rfc2119).

## Status
Each file SHALL have one of the following status:
- abandoned: not maintained, and is not useful, but still have values for reference
- active: maintained, or is used somewhere

Files SHALL be put to the folders named by these status respectively.

## Notes for Python scripts
Scripts SHOULD only use standard libraries, as they may be invoked without certain third-party libs.

If a script is using a 3rd lib, it MUST declare it in `requirements.txt`.
