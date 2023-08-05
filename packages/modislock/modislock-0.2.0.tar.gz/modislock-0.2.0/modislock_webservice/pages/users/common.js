/**
 * Created by richard on 11.04.17.
 */

/**
 * @brief Key Access / read / write / delete / edit
 * @param params
 * @param result_cb
 */
function key_access(params, result_cb) {
    // Call to server
    $.ajax({
        url: '/users/keys/' + params.user_id + '/' + params.protocol,
        type: params.type,
        data: {
            key: params.key,
            key2: params.key2,
            key3: params.key3
        }
    }).done(function(msg){
        result_cb(msg);
    });
}

/**
 *
 * @brief Generates unique ID
 * @param result_cb
 */
function generate_unique_id(result_cb) {
    $.ajax({
        url: '/users/key_gen'
    }).done(function(msg){
        result_cb(msg);
    });
}
