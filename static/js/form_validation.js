document.addEventListener("DOMContentLoaded", () => {
    initFormValidation(document);
});

document.body.addEventListener("htmx:afterSwap", (e) => {
    initFormValidation(e.target);
});

function initFormValidation(ctx) {
    ctx.querySelectorAll("form").forEach(form => {
        if (form.dataset.validationBound === "true") return;
        form.dataset.validationBound = "true";

        const fields = form.querySelectorAll("input, select, textarea");

        fields.forEach(field => {
            field.addEventListener("input", () => validateField(field));
            field.addEventListener("change", () => validateField(field));
        });

        form.addEventListener("submit", (e) => {
            let valid = true;

            fields.forEach(field => {
                if (!validateField(field)) valid = false;
            });

            if (!valid) {
                e.preventDefault();
                focusFirstError(form);
                showToast("Revisa los campos marcados");
            }
        });
    });
}

function validateField(field) {
    let valid = true;
    const value = field.value;

    // required
    if (field.hasAttribute("required") && !value) {
        valid = false;
    }

    // number > 0
    if (field.type === "number" && value) {
        if (parseFloat(value) <= 0) valid = false;
    }

    toggleFieldState(field, valid);
    return valid;
}

function toggleFieldState(field, valid) {
    field.classList.toggle("is-invalid", !valid);
    field.classList.toggle("is-valid", valid);
}

function focusFirstError(form) {
    const first = form.querySelector(".is-invalid");
    if (first) first.focus();
}