# All model fields inherited from this
from astra.validators import ForeignObjectValidatorMixin


class ModelField(object):
    # _model = None  # type: Model
    # _name = None  # type: str
    _directly_redis_helpers = ()  # Direct method helpers
    _field_type_name = '--'

    def __init__(self, **kwargs):
        if 'instance' in kwargs:
            self._name = kwargs['name']
            self._model = kwargs['model']
        self._options = kwargs

    def _get_key_name(self, is_hash=False):
        """
        Create redis key. Schema:
        prefix::object_name::field_type::id::field_name, e.g.
            prefix::user::fld::12::login
            prefix::user::list::12::sites
            prefix::user::zset::12::winners
            prefix::user::hash::54
        """
        parent_class_name = self._model.__class__.__name__.lower()
        items = [self._model._astra_prefix, parent_class_name,
                 self._field_type_name, str(self._model.pk)]
        if not is_hash:
            items.append(self._name)
        return '::'.join(items)

    def _assign(self, value, suppress_signal=False):
        raise NotImplementedError('Subclasses must implement _assign')

    def _obtain(self):
        raise NotImplementedError('Subclasses must implement _obtain')

    def _helper(self, method_name):
        if method_name not in self._directly_redis_helpers:
            raise AttributeError('Invalid attribute with name "%s"'
                                 % (method_name,))
        original_command = getattr(self._model._astra_get_db(), method_name)
        current_key = self._get_key_name()

        def _method_wrapper(*args, **kwargs):
            new_args = [current_key]
            for v in args:
                new_args.append(v)
            return original_command(*new_args, **kwargs)

        return _method_wrapper

    def _remove(self):
        self._model._astra_get_db().delete(self._get_key_name())


# Fields:
class BaseField(ModelField):
    _field_type_name = 'fld'

    def _assign(self, value, suppress_signal=False):
        if value is None:
            raise ValueError("You're cannot save None value for %s"
                             % (self._name,))

        not suppress_signal and self._model.save(
            action='pre_assign', attr=self._name, value=value)

        saved_value = self._validate(value)
        self._model._astra_get_db().set(self._get_key_name(), saved_value)

        not suppress_signal and self._model.save(
            action='post_assign', attr=self._name, value=value)

    def _obtain(self):
        value = self._model._astra_get_db().get(self._get_key_name())
        return self._convert(value)

    def _validate(self, value):
        """ Check saved value before send to server """
        raise NotImplementedError('Subclasses must implement _validate')

    def _convert(self, value):
        """ Convert server answer to user type """
        raise NotImplementedError('Subclasses must implement _convert')


# Hashes
class BaseHash(ModelField):
    _field_type_name = 'hash'

    def _assign(self, value, suppress_signal=False):
        if value is None:
            raise ValueError("You're cannot save None value for %s"
                             % (self._name,))

        not suppress_signal and self._model.save(
            action='pre_assign', attr=self._name, value=value)

        saved_value = self._validate(value)
        self._model._astra_get_db().hset(self._get_key_name(True),
                                         self._name, saved_value)
        if self._model._astra_hash_loaded:
            self._model._astra_hash[self._name] = saved_value
        self._model._astra_hash_exist = True

        not suppress_signal and self._model.save(
            action='post_assign', attr=self._name, value=value)

    def _obtain(self):
        self._load_hash()
        return self._convert(self._model._astra_hash.get(self._name, None))

    def _load_hash(self):
        if self._model._astra_hash_loaded:
            return
        self._model._astra_hash_loaded = True
        self._model._astra_hash = \
            self._model._astra_get_db().hgetall(
                self._get_key_name(True))
        if not self._model._astra_hash:  # None if hash field is not exist
            self._model._astra_hash = {}
            self._model._astra_hash_exist = False
        else:
            self._model._astra_hash_exist = True

    def _validate(self, value):
        """ Check saved value before send to server """
        raise NotImplementedError('Subclasses must implement _validate')

    def _convert(self, value):
        """ Convert server answer to user type """
        raise NotImplementedError('Subclasses must implement _convert')

    def _remove(self):
        # Delete one record on hash. _astra_hash_exist is not changes
        # eg hash may be exist
        self._model._astra_get_db().hdel(self._get_key_name(True), self._name)


# Implements for three types of lists
class BaseCollection(ForeignObjectValidatorMixin, ModelField):
    _field_type_name = ''
    _allowed_redis_methods = ()
    _single_object_answered_redis_methods = ()
    _list_answered_redis_methods = ()
    # Other methods will be answered directly

    def _obtain(self):
        return self  # for delegate to __getattr__ on this class

    def _assign(self, value, suppress_signal=False):
        if value is None:
            self._remove()
        else:
            raise ValueError('Collections fields is not possible '
                             'assign directly')

    def __getattr__(self, item):
        if item not in self._allowed_redis_methods:
            return super(BaseCollection, self).__getattribute__(item)

        original_command = getattr(self._model._astra_get_db(), item)
        current_key = self._get_key_name()

        def _method_wrapper(*args, **kwargs):
            from astra import models

            # Scan passed args and convert to pk if passed models
            new_args = [current_key]
            new_kwargs = dict()
            for v in args:
                new_args.append(v.pk if isinstance(v, models.Model) else v)
            for k, v in kwargs.items():
                new_kwargs[k] = v.pk if isinstance(v, models.Model) else v

            # Call original method on the database
            answer = original_command(*new_args, **new_kwargs)

            # Wrap to model
            if item in self._single_object_answered_redis_methods:
                return None if not answer else self._to(answer)

            if item in self._list_answered_redis_methods:
                wrapper_answer = []
                for pk in answer:
                    if not pk:
                        wrapper_answer.append(None)
                    else:
                        if isinstance(pk, tuple) and len(pk) > 0:
                            wrapper_answer.append((self._to(pk[0]), pk[1]))
                        else:
                            wrapper_answer.append(self._to(pk))

                return wrapper_answer
            return answer  # Direct answer

        return _method_wrapper
