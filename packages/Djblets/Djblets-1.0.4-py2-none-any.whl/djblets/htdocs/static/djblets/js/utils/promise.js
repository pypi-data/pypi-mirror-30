"use strict";

/**
 * Return a new promise with its resolver.
 *
 * Returns:
 *     array:
 *     An array of the promise and its resolver.
 */
Promise.withResolver = function withResolver() {
    var resolver = void 0;
    var promise = new Promise(function (resolve, reject) {
        resolver = resolve;
    });

    return [promise, resolver];
};

//# sourceMappingURL=promise.js.map