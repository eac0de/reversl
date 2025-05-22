document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("edit-permissions-form");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const checkboxes = document.querySelectorAll('input[name="permissions"]:checked');
    const permission_codes = Array.from(checkboxes).map((cb) => cb.value);

    fetch(window.urlForUpdateUserPermissions, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": window.csrfToken,
      },
      body: JSON.stringify({ permission_codes }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("HTTP error " + res.status);
        return res.json();
      })
      .then((data) => {
        for (let key of Object.keys(window.permissionCodeNameMap)) {
          console.log("perm-" + key);
          permFromForm = document.getElementById("form-perm-" + key);
          perm = document.getElementById("perm-" + key);
          if (data.permission_codes.includes(key)) {
            permFromForm.checked = true;
            perm.classList = "bi bi-check";
          } else {
            permFromForm.checked = false;
            perm.classList = "bi bi-x";
          }
        }
        const modal = bootstrap.Modal.getInstance(document.getElementById("editPermissionsModal"));
        modal.hide();
      })
      // .catch((err) => {
      //   alert("Failed: " + err.message);
      // });
  });
});
