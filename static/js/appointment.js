document.addEventListener("DOMContentLoaded", function () {
  const config = window.APPT_CONFIG || {};
  const state = {
    service: null,
    serviceLabel: null,
    duration: null,
    date: null,
    time: null,
  };
  const stepEls = document.querySelectorAll(".mld-step");
  const panels = document.querySelectorAll(".mld-panel");

  function goTo(stepNum) {
    panels.forEach((p) => p.classList.remove("active"));
    document.getElementById("panel-" + stepNum).classList.add("active");
    stepEls.forEach((s) => {
      const n = Number(s.dataset.step);
      s.classList.toggle("active", n === stepNum);
      s.classList.toggle("done", n < stepNum);
    });
    if (stepNum === 3) checkStep3();
    document
      .getElementById("book")
      .scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Step 1: service selection
  document.querySelectorAll(".mld-service").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".mld-service")
        .forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      state.service = btn.dataset.code;
      state.serviceLabel = btn.dataset.name;
      state.duration = btn.dataset.dur;
      document.getElementById("toStep2").disabled = false;
    });
  });
  document.getElementById("toStep2").addEventListener("click", () => goTo(2));

  // Step 2: date & time
  const dateInput = document.getElementById("apptDate");
  const today = new Date().toISOString().split("T")[0];
  dateInput.min = today;
  dateInput.addEventListener("change", () => {
    state.date = dateInput.value;
    checkStep2();
  });

  document.querySelectorAll(".mld-slot:not(.taken)").forEach((slot) => {
    slot.addEventListener("click", () => {
      document
        .querySelectorAll(".mld-slot")
        .forEach((s) => s.classList.remove("selected"));
      slot.classList.add("selected");
      state.time = slot.textContent.trim();
      document.getElementById("selectedTimeDisplay").value = state.time;
      checkStep2();
    });
  });
  function checkStep2() {
    document.getElementById("toStep3").disabled = !(state.date && state.time);
  }
  document.getElementById("toStep3").addEventListener("click", () => goTo(3));

  // Step 3: patient selection + optional new dependent
  const patientSelect = document.getElementById("patientSelect");
  const newDependentForm = document.getElementById("newDependentForm");
  const notesInput = document.getElementById("notes");

  patientSelect.addEventListener("change", () => {
    newDependentForm.style.display =
      patientSelect.value === "__new__" ? "flex" : "none";
    checkStep3();
  });

  document.getElementById("saveDependent").addEventListener("click", () => {
    const firstName = document.getElementById("depFirstName").value.trim();
    const lastName = document.getElementById("depLastName").value.trim();
    const dob = document.getElementById("depDob").value;

    if (!firstName || !dob) {
      alert("First name and date of birth are required.");
      return;
    }

    fetch(config.addDependentUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": config.csrfToken,
      },
      body: new URLSearchParams({
        first_name: firstName,
        last_name: lastName,
        date_of_birth: dob,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (!data.ok) {
          alert(data.error || "Couldn't add family member.");
          return;
        }
        const option = document.createElement("option");
        option.value = data.patient.id;
        option.textContent = data.patient.label;
        patientSelect.insertBefore(
          option,
          patientSelect.querySelector('option[value="__new__"]'),
        );
        patientSelect.value = data.patient.id;
        newDependentForm.style.display = "none";
        document.getElementById("depFirstName").value = "";
        document.getElementById("depLastName").value = "";
        document.getElementById("depDob").value = "";
        checkStep3();
      })
      .catch(() =>
        alert(
          "Something went wrong adding that family member. Please try again.",
        ),
      );
  });

  function checkStep3() {
    const valid = patientSelect.value && patientSelect.value !== "__new__";
    document.getElementById("toStep4").disabled = !valid;
  }
  checkStep3(); // run once immediately, since a patient may already be pre-selected on load
  document.getElementById("toStep4").addEventListener("click", () => {
    buildSummary();
    goTo(4);
  });

  function buildSummary() {
    const dateObj = state.date ? new Date(state.date + "T00:00:00") : null;
    const prettyDate = dateObj
      ? dateObj.toLocaleDateString(undefined, {
          weekday: "long",
          month: "long",
          day: "numeric",
        })
      : "";
    const patientLabel =
      patientSelect.options[patientSelect.selectedIndex].textContent;
    document.getElementById("summaryBox").innerHTML = `
      <dt>Service</dt><dd>${state.serviceLabel} <span class="mono" style="color:var(--ink-soft); font-weight:400;">(${state.duration})</span></dd>
      <dt>When</dt><dd>${prettyDate} at ${state.time}</dd>
      <dt>Patient</dt><dd>${patientLabel}</dd>
    `;
  }

  // Step 4: confirm — actually submits to the backend
  const confirmBtn = document.getElementById("confirmBtn");
  confirmBtn.addEventListener("click", () => {
    confirmBtn.disabled = true;
    confirmBtn.textContent = "Booking...";

    fetch(config.bookUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": config.csrfToken,
      },
      body: new URLSearchParams({
        patient_id: patientSelect.value,
        service: state.service,
        date: state.date,
        time: state.time,
        notes: notesInput.value,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        confirmBtn.disabled = false;
        confirmBtn.textContent = "Confirm appointment";

        if (!data.ok) {
          alert(
            data.error || "Couldn't book that appointment. Please try again.",
          );
          return;
        }
        const a = data.appointment;
        document.getElementById("confirmText").textContent =
          `We've booked ${a.patient} for a ${a.service.toLowerCase()} on ${a.date} at ${a.time}. A confirmation will follow by email.`;
        goTo(5);
      })
      .catch(() => {
        confirmBtn.disabled = false;
        confirmBtn.textContent = "Confirm appointment";
        alert(
          "Something went wrong. Please check your connection and try again.",
        );
      });
  });

  // Back buttons
  document.querySelectorAll("[data-back]").forEach((btn) => {
    btn.addEventListener("click", () => goTo(Number(btn.dataset.back)));
  });

  // Restart
  document.getElementById("restartBtn").addEventListener("click", () => {
    state.service =
      state.serviceLabel =
      state.duration =
      state.date =
      state.time =
        null;
    document
      .querySelectorAll(".mld-service, .mld-slot")
      .forEach((el) => el.classList.remove("selected"));
    document.getElementById("selectedTimeDisplay").value = "";
    dateInput.value = "";
    patientSelect.selectedIndex = 0;
    newDependentForm.style.display = "none";
    notesInput.value = "";
    document.getElementById("toStep2").disabled = true;
    document.getElementById("toStep3").disabled = true;
    document.getElementById("toStep4").disabled = true;
    goTo(1);
  });
});
