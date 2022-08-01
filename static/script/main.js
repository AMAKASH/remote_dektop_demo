const submit = document.getElementById("submit_button");

submit.addEventListener("click", () => {
  let username = document.getElementById("username").value;
  let pass = document.getElementById("pass").value;

  console.log(username);
  console.log(pass);

  let xhr = new XMLHttpRequest();
  xhr.open("POST", "./auth", true);
  xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
  // send the collected data as JSON
  xhr.send(JSON.stringify({ _key: username, _secret: pass }));
  xhr.onloadend = function () {
    const res = xhr.response;
    console.log(res);

    if (res == "ok") {
      const form = document.getElementById("formcontainer");
      form.classList.add("hidden");
      load_remote(username, pass);
    } else {
      console.log("Invaid Auth");
      alert("Username or password incorrect");
    }
  };
});

const load_remote = (KEY, secret) => {
  const img = document.querySelector("img");

  let filename = "undefined"; // keep it string
  const loop = () => {
    fetch("./rd", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        __: Date.now(),
        filename: filename,
        _key: KEY,
        _secret: secret,
      }),
    })
      .then(function (response) {
        console.log(response);
        if (response.redirected) {
          window.location.href = response.url;
        }
        filename = response.headers.get("filename");
        return response.blob();
      })
      .then(function (myBlob) {
        //console.log(myBlob)
        if (myBlob.size) {
          let objectURL = URL.createObjectURL(myBlob);
          img.src = objectURL;
        } else {
          console.log("img not change");
        }
      })
      .catch((err) => console.error(err));
  };

  let setIntervalId = window.setInterval(loop, 200);

  //'click mousemove keypress drag mousewheel mousedown mouseup'
  let postEvent = (payload) => {
    console.log(payload);
    payload._key = KEY;
    payload._secret = secret;
    // construct an HTTP request
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "./event_post", true);
    xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    // send the collected data as JSON
    xhr.send(JSON.stringify(payload));
    xhr.onloadend = function () {
      // done
    };
  };

  img.addEventListener("click", (event) => {
    let payload = {
      type: event.type,
      x: event.clientX,
      y: event.clientY,
    };
    postEvent(payload);
  });

  document.onkeydown = (event) => {
    let payload = {
      type: event.type,
      ctrlKey: event.ctrlKey,
      altKey: event.altKey,
      shiftKey: event.shiftKey,
      key: event.key,
    };
    postEvent(payload);
    event.preventDefault();
  };
};
