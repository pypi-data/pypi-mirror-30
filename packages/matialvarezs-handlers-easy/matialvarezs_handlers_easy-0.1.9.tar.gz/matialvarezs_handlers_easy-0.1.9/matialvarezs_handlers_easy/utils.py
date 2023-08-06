import simplejson as json

def delete_db_object(method_delete,**kwargs,**options):
    # method_delete => return object if exists or none
    message_ok_delete = options.get('message_ok_delete','delete ok')
    message_error_on_delete = options.get('message_error_on_delete','error on delete')
    db_object = method_delete(**kwargs)
    if db_object:
        db_object.delete()
        return json.dumps({"results": message_ok_delete, "error": None})
    return json.dumps({"results": None, "error": message_error_on_delete})