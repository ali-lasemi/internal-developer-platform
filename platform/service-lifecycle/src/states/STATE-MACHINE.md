# Lifecycle State Machine

## States

CREATED

↓

DEVELOPMENT

↓

TESTING

↓

PRODUCTION

↓

MAINTENANCE

↓

RETIRED


## Rules

A service cannot skip required lifecycle stages without approval.


Every transition requires:

- Validation
- Authorization
- Audit record
- Notification
