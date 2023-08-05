import os
import six
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


def queryset_csv_export(qs, fields, cache_funcs=None, filepath=None, fileobj=None, delimiter='|'):
    import csv
    import inspect
    from django.db.models.query import QuerySet

    if not filepath:
        raise Exception("expecting a filepath")
    file_dir = os.path.dirname(filepath)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    csvfile = fileobj or open(filepath, 'w')  # will write to disk by default
    writer = csv.writer(csvfile, delimiter=delimiter)

    def to_string(val):
        if val is None:
            val = ""
        if callable(val):
            val = val()
        if not isinstance(val, six.string_types):
            val = str(val)
        # try:
        #     val = ascii_encode(val)
        # except:
        #     val = str(val)

        return ("%r" % val)[1:-1]

    def get_arg_count(fn):
        from functools import partial
        if type(fn) == partial:
            return len(inspect.getargspec(fn.func)[0]) - len(fn.args)
        return len(inspect.getargspec(fn)[0])

    header_names = []

    rows = []
    import types
    if isinstance(qs, list):
        total_count = len(qs)
    elif isinstance(qs, QuerySet):
        total_count = qs.count()
    elif isinstance(qs, types.GeneratorType):
        total_count = "unknown (generator)"
    else:
        raise Exception("No one has shown me how to get the count of a %s" % type(qs))
    logger.debug("# of rows in qs = %s" % total_count)
    count = 0
    for obj in qs:
        count += 1
        start_time = timezone.now()
        row = []
        cache_dict = {}
        if cache_funcs:
            def is_cache_evaluated():
                all_cache_keys = [cache_func[0] for cache_func in cache_funcs]
                return all([cache_key in cache_dict for cache_key in all_cache_keys])
            while not is_cache_evaluated():
                for cache_func_tpl in cache_funcs:
                    cache_key, cache_func = cache_func_tpl[0], cache_func_tpl[1]
                    cache_dependency = cache_func_tpl[2] if len(cache_func_tpl) > 2 else None
                    if cache_key in cache_dict or (cache_dependency is not None and cache_dependency not in cache_dict):
                        continue
                    cache_func_arg_count = get_arg_count(cache_func)
                    if cache_func_arg_count == 1:
                        cache_dict[cache_key] = cache_func(obj)
                    elif cache_func_arg_count == 2:
                        cache_dict[cache_key] = cache_func(obj, cache_dict)
                    else:
                        raise Exception("invalid number of args for cache function")
        for field in fields:
            if isinstance(field, six.string_types):
                if field not in header_names:
                    header_names.append(field)
                if isinstance(obj, dict):
                    val = obj.get(field, "")
                else:
                    val = getattr(obj, field, "")
                row.append(to_string(val))  # append the value as a raw text value to keep linebreaks \r\n on a single line
            elif isinstance(field, tuple):
                if len(field) != 2:
                    raise Exception("invalid computed field length of %s. Field value = %s" % (len(field), field))
                computed_header_name, fn = field
                if computed_header_name not in header_names:
                    header_names.append(computed_header_name)
                fn_arg_count = get_arg_count(fn)
                if fn_arg_count == 1:
                    row.append(to_string(fn(obj)))
                elif fn_arg_count == 2:
                    row.append(to_string(fn(obj, cache_dict)))
                else:
                    raise Exception("expecting 1 or 2 args. actual # = %s" % fn_arg_count)
            else:
                raise Exception("invalid field type of %s, field value = %s" % (type(field), field))

        rows.append(row)
        end_time = timezone.now()
        logger.debug("finished %s of %s. time = %s" % (count, total_count, str(end_time - start_time)))

    writer.writerow(header_names)
    writer.writerows(rows)

    if fileobj:
        return fileobj


# def ascii_encode(string):
#     import unicodedata
#     return unicodedata.normalize('NFKD', unicode(string)).encode('ascii', 'ignore')
