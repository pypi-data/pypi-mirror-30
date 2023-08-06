define(function() {
    "use strict";

    window['requirejs'].config({
        map: {
            '*': {
                'pypsea': 'nbextensions/pypsea/index',
            },
        }
    });
    // Export the required load_ipython_extention
    return {
        load_ipython_extension : function() {}
    };
});
