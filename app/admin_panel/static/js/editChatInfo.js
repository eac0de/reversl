document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("edit-chat-form");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    let formData = new FormData(form);
    formData.append("csrf_token", window.csrfToken);

    formData.set("first_name", formData.get("first_name").trim());
    if (formData.get("first_name") == "") {
      formData.delete("first_name");
    }

    formData.set("last_name", formData.get("last_name").trim());
    if (formData.get("last_name") == "") {
      formData.delete("last_name");
    }

    formData.set("patronymic_name", formData.get("patronymic_name").trim());
    if (formData.get("patronymic_name") == "") {
      formData.delete("patronymic_name");
    }

    formData.set("email", formData.get("email").trim());
    if (formData.get("email") == "") {
      formData.delete("email");
    }

    formData.set("phone_number", formData.get("phone_number").trim());
    if (formData.get("phone_number") == "") {
      formData.delete("phone_number");
    }

    fetch(window.urlForUpdateChatInfo, {
      method: "PATCH",
      body: formData,
    })
      .then((res) => {
        if (!res.ok) throw new Error("HTTP error " + res.status);
        return res.json();
      })
      .then((data) => {
        document.getElementById("chat-first-name").textContent = data.first_name || "-";
        document.getElementById("chat-last-name").textContent = data.last_name || "-";
        document.getElementById("chat-patronymic-name").textContent = data.patronymic_name || "-";
        document.getElementById("chat-email").textContent = data.email || "-";
        document.getElementById("chat-phone-number").textContent = data.phone_number || "-";

        document.getElementById("form-chat-first-name").value = data.first_name || "";
        document.getElementById("form-chat-last-name").value = data.last_name || "";
        document.getElementById("form-chat-patronymic-name").value = data.patronymic_name || "";
        document.getElementById("form-chat-email").value = data.email || "";
        document.getElementById("form-chat-phone-number").value = data.phone_number || "";

        const modal = bootstrap.Modal.getInstance(document.getElementById("editChatModal"));
        modal.hide();
      })
      .catch((err) => {
        console.log(err);
        alert("Failed: " + err.message);
      });
  });
});
