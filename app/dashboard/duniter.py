CERTIFICATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "pubkey": {"type": "string"},
        "uid": {"type": "string"},
        "isMember": {"type": "boolean"},
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pubkey": {"type": "string"},
                    "uid": {"type": "string"},
                    "cert_time": {
                        "type": "object",
                        "properties": {
                            "block": {"type": "number"},
                            "medianTime": {"type": "number"},
                        },
                        "required": ["block", "medianTime"],
                    },
                    "sigDate": {"type": "string"},
                    "written": {
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "number": {"type": "number"},
                                    "hash": {"type": "string"},
                                },
                                "required": ["number", "hash"],
                            },
                            {"type": "null"},
                        ]
                    },
                    "isMember": {"type": "boolean"},
                    "wasMember": {"type": "boolean"},
                    "signature": {"type": "string"},
                },
                "required": [
                    "pubkey",
                    "uid",
                    "cert_time",
                    "sigDate",
                    "written",
                    "wasMember",
                    "isMember",
                    "signature",
                ],
            },
        },
    },
    "required": ["pubkey", "uid", "isMember", "certifications"],
}
