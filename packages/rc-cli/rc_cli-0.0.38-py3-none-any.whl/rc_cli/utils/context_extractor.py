def get_config(context):
    """
    Helper method extract config from click.Context

    :param context: Context object passed in by Click\n
    :return: Config object within Context
    """
    return context.obj.get('config')