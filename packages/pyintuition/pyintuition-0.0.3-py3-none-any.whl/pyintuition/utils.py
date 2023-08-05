def prefix_field_names(record: dict) -> dict:
    """Prefix fields with '_fnm_' for QuickBase."""
    for field in record.keys():
        # Don't prefix rid, it isn't a field name for us
        if field == 'rid':
            pass
        
        record[f'_fnm_{field}'] = record.pop(field)
        return record
