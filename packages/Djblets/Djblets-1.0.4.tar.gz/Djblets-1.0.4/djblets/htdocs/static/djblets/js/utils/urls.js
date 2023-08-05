'use strict';

/**
 * Build and return a URL out of different components.
 *
 * This will construct a URL based on a base URL (which may be an absolute
 * URL, a relative path, or an empty string), optional query string data (as
 * a string, a dictionary, or array), and an optional anchor name.
 *
 * Args:
 *     options (object):
 *         The options used to construct the URL.
 *
 * Option Args:
 *     anchor (unicode, optional):
 *         An anchor to append to the URL. This may include the leading ``#``,
 *         but it's optional.
 *
 *     baseURL (string, optional):
 *         The base URL to build onto, if any. If not provided, an empty
 *         string will be used.
 *
 *     queryData (*, optional):
 *         Data for the query string. This can be a string, an object, or
 *         an array of dictionaries containing ``name`` and ``value`` keys.
 *         See :js:func:`jQuery.param` for information on what's allowed here.
 *
 *         If using an object of keys and values, the sort order is not
 *         guaranteed. It will be up to the JavaScript engine. Provide a
 *         string or array to guarantee order.
 *
 *         If using a string, and the string begins with a ``?``, it will be
 *         stripped away.
 *
 * Returns:
 *     string:
 *     The resulting URL.
 */
Djblets.buildURL = function () {
    var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

    var url = options.baseURL || '';

    /* Build the query string, if any. */
    var queryData = options.queryData;

    if (queryData) {
        var queryString = void 0;

        if (typeof queryData === 'string') {
            queryString = queryData;

            if (queryString.indexOf('?') === 0) {
                queryString = queryString.substr(1);
            }
        } else {
            queryString = $.param(queryData);
        }

        if (queryString) {
            url += '?' + queryString;
        }
    }

    /* Append an anchor, if any. */
    var anchor = options.anchor;

    if (anchor) {
        if (anchor.indexOf('#') === 0) {
            url += anchor;
        } else {
            url += '#' + anchor;
        }
    }

    return url;
};

/**
 * Parse a query string for key/value pairs.
 *
 * This takes a query string in the provided URL and parses it for standard
 * key/value pairs, returning an object representing those keys and values.
 * It can handle keys without values and optionally store multiple values
 * listed for the same key.
 *
 * Args:
 *     url (string):
 *         The URL containing a query string to parse.
 *
 *     options (object, optional):
 *         Options for controlling the parsing.
 *
 * Option Args:
 *     allowMultiValue (boolean):
 *         Whether to store multiple values for the same key, if found in
 *         the query string. The value for such a key will be an array of all
 *         values. If ``false`` (the default), only last value for a key will
 *         be stored.
 *
 * Returns:
 *     object:
 *     The resulting keys and values representing the query string.
 *
 *     If there was a query string item that did not have a value (in other
 *     words, no ``=`` was present), then its value will be ``null``.
 *
 *     If ``options.allowMultiValue`` is ``true``, and a key was used more
 *     than once, then its value will be a list of all values in the query
 *     string for that key.
 */
Djblets.parseQueryString = function (url) {
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

    var allowMultiValue = options.allowMultiValue;

    var j = url.indexOf('?');
    var queryString = void 0;

    if (j === -1) {
        /* Assume the whole thing is a query string. */
        queryString = url;
    } else {
        queryString = url.substr(j + 1);
    }

    var query = {};

    if (queryString.length === 0) {
        return query;
    }

    var queryParams = queryString.split('&');

    for (var i = 0; i < queryParams.length; i++) {
        var queryParam = queryParams[i];
        var key = void 0;
        var value = void 0;

        j = queryParam.indexOf('=');

        if (j === -1) {
            key = decodeURIComponent(queryParam);
            value = null;
        } else {
            key = decodeURIComponent(queryParam.substr(0, j));
            value = decodeURIComponent(queryParam.substr(j + 1));
        }

        if (allowMultiValue && query.hasOwnProperty(key)) {
            if (_.isArray(query[key])) {
                query[key].push(value);
            } else {
                query[key] = [query[key], value];
            }
        } else {
            query[key] = value;
        }
    }

    return query;
};

//# sourceMappingURL=urls.js.map