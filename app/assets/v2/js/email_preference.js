class EmailPreferenceEvent {

  static send(data) {

    let loggingApi = `api/v1/email_preference_log/`;

    fetch(loggingApi, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (result) {
        console.log(result);
      })
      .catch(function (error) {
        console.log("Request failed", error);
      });
  }

  static createEvent(...obj) {
    let baseObj = {
      email: document.contxt.email,
      customObjects: {},
    };
    baseObj.customObjects["data"] = obj;
    this.send(baseObj);
  }
}
