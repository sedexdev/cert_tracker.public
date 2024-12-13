/**
 * Toggles the dark class in the document
 */
function toggleDarkMode() {
  // use local storage to persist dark mode
  if (!window.localStorage.getItem("darkMode")) {
    window.localStorage.setItem("darkMode", "on");
  } else {
    window.localStorage.removeItem("darkMode");
  }
  document.documentElement.classList.toggle("dark");
}

/**
 * Displays the add content buttons on all tabs
 * except statistics as this just displays stats
 * about the content state
 *
 * @param {string} value tab to show button under
 */
function displayAddContentButton(value) {
  const addBtn = document.getElementById("content-btn");
  const importBtn = document.getElementById("import-btn");
  if (value != "statistics") {
    addBtn.classList.remove("hidden");
    importBtn.classList.remove("hidden");
  } else {
    addBtn.classList.add("hidden");
    importBtn.classList.add("hidden");
  }
}

/**
 * Hides the add content buttons
 */
function hideAddContentButton() {
  const addBtn = document.getElementById("content-btn");
  const importBtn = document.getElementById("import-btn");
  addBtn.classList.add("hidden");
  importBtn.classList.add("hidden");
}

/**
 * Hides all content
 */
function hideAllContent() {
  const courses = document.getElementById("courses");
  const videos = document.getElementById("videos");
  const articles = document.getElementById("articles");
  const documents = document.getElementById("documentation");
  const content = [courses, videos, articles, documents];
  for (let topic of content) {
    topic.classList.add("hidden");
  }
}

/**
 * Clears the values in the name and url form
 * input fields
 */
function clearFormInputs() {
  const name = document.getElementById("resource-name");
  const url = document.getElementById("resource-url");
  if (name && url) {
    name.value = "";
    url.value = "";
  }
}

/**
 * Clears resource type radio buttons of the
 * checked attribute
 */
function clearChecked() {
  for (let i = 0; i < 4; i++) {
    const el = document.getElementById(`resource_type-${i}`);
    el.checked = false;
  }
}

/**
 * Displays the selected content
 *
 * @param {number} id element to display
 */
function displayContent(id) {
  const content = [
    "statistics",
    "courses",
    "videos",
    "articles",
    "documentation",
  ];
  for (let topic of content) {
    const el = document.getElementById(topic);
    if (topic == id) {
      el.classList.remove("hidden");
    } else {
      el.classList.add("hidden");
    }
  }
}

/**
 * Updates the highlighting for the selected
 * content when selected from the nav bar
 *
 * @param {HTMLElement} el element to update
 */
function updateHighlightNav(el) {
  let links = document.getElementById("cert-nav").children;
  // remove selected class
  for (let link of links) {
    if (link.classList.contains("selected")) {
      link.classList.remove("selected");
    }
  }
  el.classList.add("selected");
  const select_list = document.getElementById("content");
  select_list.value = el.innerHTML.toLowerCase();
}

/**
 * Updates the highlighting for the selected
 * content when selected from the select list
 *
 * @param {str} value
 */
function updateHighlightSelect(value) {
  let links = document.getElementById("cert-nav").children;
  // remove selected class
  for (let link of links) {
    if (link.innerHTML.toLowerCase() == value) {
      link.classList.add("selected");
    } else {
      link.classList.remove("selected");
    }
  }
}

/**
 * Handles the cert content nav selection
 *
 * @param {HTMLElement} el
 */
function handleNav(el) {
  // hide any open forms
  hideResourceForm("resource-form");
  hideResourceForm("resource-import-form");
  // clear the radio buttons
  clearChecked();
  let id;
  if (el.tagName.toLowerCase() == "select") {
    displayAddContentButton(el.value);
    updateHighlightSelect(el.value);
    id = el.value;
  } else {
    const value = el.innerHTML.toLowerCase();
    displayAddContentButton(value);
    updateHighlightNav(el);
    id = value;
  }
  displayContent(id);
  // update local storage
  window.localStorage.setItem("currentNav", id);
}

/**
 *
 * Displays the resource form to add content
 * to the cert dashboard
 *
 * @param {string} id
 */
function displayResourceForm(id) {
  let links = document.getElementById("cert-nav").children;
  // get value of selected content
  for (let link of links) {
    if (link.classList.contains("selected")) {
      type = link.innerHTML.toLowerCase();
    }
  }
  // hide other elements and only display form
  hideAllContent();
  hideAddContentButton();
  const form = document.getElementById(id);
  form.classList.remove("hidden");
  // clear the input fields
  clearFormInputs();
}

/**
 * Gets the innerHTML value of the currently
 * selected content tab
 */
function getSelectedValue() {
  let value;
  let links = document.getElementById("cert-nav").children;
  // find selected element value
  for (let link of links) {
    if (link.classList.contains("selected")) {
      value = link.innerHTML.toLowerCase();
      break;
    }
  }
  return value;
}

/**
 * Closes the resource form and displays the content
 *
 * @param {string} id
 */
function hideResourceForm(id) {
  const el = document.getElementById(id);
  el.classList.add("hidden");
  // display the add content button
  const value = getSelectedValue();
  displayAddContentButton(value);
  // display the content
  displayContent(value);
}

/**
 * Updates local storage with the display state of the
 * resource form
 */
function updateResourceFormState(state) {
  window.localStorage.setItem("loadResourceForm", state);
}

/**
 * Displays the exam date update form
 */
function displayExamForm() {
  const form = document.getElementById("exam-date-form");
  if (form) {
    const reminderBtn = document.getElementById("set-reminder-btn");
    const container = document.getElementById("exam-date-container");
    form.classList.remove("hidden");
    reminderBtn.classList.add("hidden");
    container.classList.add("hidden");
    const delReminderBtn = document.getElementById("del-reminder-btn");
    if (delReminderBtn) {
      delReminderBtn.classList.add("hidden");
    }
  }
}

/**
 * Hides the exam date update form
 */
function hideExamForm() {
  const form = document.getElementById("exam-date-form");
  if (form) {
    const reminderBtn = document.getElementById("set-reminder-btn");
    const container = document.getElementById("exam-date-container");
    form.classList.add("hidden");
    reminderBtn.classList.remove("hidden");
    container.classList.remove("hidden");
    const delReminderBtn = document.getElementById("del-reminder-btn");
    if (delReminderBtn) {
      delReminderBtn.classList.remove("hidden");
    }
  }
}

/**
 * Displays the update cert form
 *
 * @param {string} id
 */
function displayUpdateCert(e, id) {
  e.preventDefault();
  const el = document.getElementById(`cert-update-form-${id}`);
  if (el && e.stopPropagation) {
    e.stopPropagation();
    el.classList.remove("hidden");
  }
}

/**
 * Hides the update cert form
 *
 * @param {string} id
 */
function hideUpdateCert(id) {
  const el = document.getElementById(`cert-update-form-${id}`);
  if (el) {
    el.classList.add("hidden");
  }
}

/**
 * Displays the update resource form
 *
 * @param {string} id
 * @param {string} type
 */
function displayUpdateResource(e, id, type) {
  e.preventDefault();
  const el = document.getElementById(`resource-update-form-${id}`);
  if (el && e.stopPropagation) {
    e.stopPropagation();
    el.classList.remove("hidden");
    // set radio button to checked
    const span = document.getElementById(`update-radio-btn-${type}-${id}`);
    const btn = span.children[0];
    btn.setAttribute("checked", "checked");
  }
}

/**
 * Hides the update resource form
 *
 * @param {string} id
 */
function hideUpdateResource(id) {
  const el = document.getElementById(`resource-update-form-${id}`);
  if (el) {
    el.classList.add("hidden");
  }
}

/**
 * Displays the update section form
 *
 * @param {string} id
 * @param {string} resourceId
 */
function displayUpdateSection(e, id, resourceId) {
  e.preventDefault();
  const el = document.getElementById(`section-update-form-${id}-${resourceId}`);
  if (el && e.stopPropagation) {
    e.stopPropagation();
    el.classList.remove("hidden");
  }
}

/**
 * Hides the update section form
 *
 * @param {string} id
 * @param {string} resourceId
 */
function hideUpdateSection(id, resourceId) {
  const el = document.getElementById(`section-update-form-${id}-${resourceId}`);
  if (el) {
    el.classList.add("hidden");
  }
}

/**
 * Displays the set reminder form
 *
 * @param {string} id
 */
function displaySetReminderForm(id) {
  const formEl = document.getElementById(id);
  if (formEl) {
    const reminderBtn = document.getElementById("set-reminder-btn");
    const examDate = document.getElementById("exam-date-container");
    const plotly = document.getElementById("plotly-dash-container");
    reminderBtn.classList.add("hidden");
    examDate.classList.add("hidden");
    plotly.classList.add("hidden");
    formEl.classList.remove("hidden");
    const delReminderBtn = document.getElementById("del-reminder-btn");
    if (delReminderBtn) {
      delReminderBtn.classList.add("hidden");
    }
  }
}

/**
 * Hides the set reminder form
 *
 * @param {string} id
 */
function hideSetReminderForm(id) {
  const formEl = document.getElementById(id);
  if (formEl) {
    const reminderBtn = document.getElementById("set-reminder-btn");
    const examDate = document.getElementById("exam-date-container");
    const plotly = document.getElementById("plotly-dash-container");
    reminderBtn.classList.remove("hidden");
    examDate.classList.remove("hidden");
    plotly.classList.remove("hidden");
    formEl.classList.add("hidden");
    const delReminderBtn = document.getElementById("del-reminder-btn");
    if (delReminderBtn) {
      delReminderBtn.classList.remove("hidden");
    }
  }
}
