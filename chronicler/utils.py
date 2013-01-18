''' Audit utilities '''

def get_data_from_field(obj, field):
    ''' Takes an model obj and a field object, gets the value for the field
    from the supplied object and returns the resulting data
    '''
    field_type = field.get_internal_type()
    if field_type == 'ForeignKey':
        return getattr(obj, field.attname)
    elif field_type == 'DateTimeField':
        return str(getattr(obj, field.name))
    else:
        return getattr(obj, field.name)

def serialize_data(instance, relations):
    ''' Gets the data from every standard field and places it in the data
    dictionary. Then proceeds to inspect the relations list provided, and
    grabs all the necessary data by following those relations. When complete
    returns the data dictionary to be serialized
    '''
    data = {}
    for field in instance._meta.fields:
        data[field.name] = get_data_from_field(instance, field)

    for relation in relations:
        related_attr = getattr(instance, relation)
        data[relation] = []
        for item in related_attr.all():
            relation_data = {}
            for field in item._meta.fields:
                relation_data[field.name] = get_data_from_field(
                        item, field)
            data[relation].append(relation_data)

    return data

def data_has_changes(obj, relations, prev_audit=None):
    ''' Compares an obj to the previous audit item we created. If the
    serialized differs, return True. Otherwise, we return False.
    '''
    if not prev_audit:
        return True
    data = serialize_data(obj, relations)
    return data != prev_audit.audit_data
