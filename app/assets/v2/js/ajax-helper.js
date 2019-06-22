/**
 * Generic function to make an AJAX call avoid DRY
 *
 * ex:
 * var getdata = fetchData('/api/v0.1/data/','GET')
 * $.when(getdata).then(function(response){ return response })
 *
 * var sendForm = fetchData(e.currentTarget.action,
 *              e.currentTarget.method,
 *              $("#form-wallets").serialize()
 *            )
 * $.when(sendForm).then(function(payback){ return payback })
 *
*/

var fetchData = function(urlRequest, methodType, data, headers) {
  // Return the $.ajax promise
  return $.ajax({
    url: urlRequest,
    type: methodType,
    headers: headers,
    dataType: 'json',
    data: data
  });
};
