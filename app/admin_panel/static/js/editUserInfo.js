document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("edit-user-form");

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

    formData.set("phone_number", formData.get("phone_number").trim());
    if (formData.get("phone_number") == "") {
      formData.delete("phone_number");
    }

    fetch(window.urlForUpdateUserInfo, {
      method: "PATCH",
      body: formData,
    })
      .then((res) => {
        if (!res.ok) throw new Error("HTTP error " + res.status);
        return res.json();
      })
      .then((data) => {
        document.getElementById("user-first-name").textContent = data.first_name || "-";
        document.getElementById("user-last-name").textContent = data.last_name || "-";
        document.getElementById("user-patronymic-name").textContent = data.patronymic_name || "-";
        document.getElementById("user-email").textContent = data.email || "-";
        document.getElementById("user-phone-number").textContent = data.phone_number || "-";

        document.getElementById("form-user-first-name").value = data.first_name || "";
        document.getElementById("form-user-last-name").value = data.last_name || "";
        document.getElementById("form-user-patronymic-name").value = data.patronymic_name || "";
        document.getElementById("form-user-email").value = data.email || "";
        document.getElementById("form-user-phone-number").value = data.phone_number || "";

        const modal = bootstrap.Modal.getInstance(document.getElementById("editUserModal"));
        modal.hide();
      })
      .catch((err) => {
        alert("Failed: " + err.message);
      });
  });
});
