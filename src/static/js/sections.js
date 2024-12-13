/**
 * Displays the section form to add a section
 * to a course
 *
 * @param {str} id
 */
function displaySectionForm(id) {
  const sections = document.getElementById(`sections-${id}-form`);
  const addBtn = document.getElementById(`sections-${id}-btn`);
  const importJsonBtn = document.getElementById(`sections-${id}-import-btn`);
  const closeBtn = document.getElementById(`sections-${id}-close-btn`);
  sections.classList.remove("hidden");
  addBtn.classList.add("hidden");
  importJsonBtn.classList.add("hidden");
  closeBtn.classList.remove("hidden");
}

/**
 * Closes the section form
 *
 * @param {number} id element ID
 */
function hideSectionForm(id) {
  const sections = document.getElementById(`sections-${id}-form`);
  const addBtn = document.getElementById(`sections-${id}-btn`);
  const importJsonBtn = document.getElementById(`sections-${id}-import-btn`);
  const closeBtn = document.getElementById(`sections-${id}-close-btn`);
  sections.classList.add("hidden");
  addBtn.classList.remove("hidden");
  importJsonBtn.classList.remove("hidden");
  closeBtn.classList.add("hidden");
}

/**
 * Displays course section data
 *
 * @param {number} id
 */
function displaySections(id) {
  const down = document.getElementById(`down-arrow-${id}`);
  const up = document.getElementById(`up-arrow-${id}`);
  const sections = document.getElementById(`sections-${id}`);
  const courses = window.localStorage.getItem("coursesWithOpenSections");
  // create the courses array if not found
  if (!courses) {
    window.localStorage.setItem(
      "coursesWithOpenSections",
      JSON.stringify([id])
    );
  }
  if (down.classList.contains("hidden")) {
    down.classList.remove("hidden");
    up.classList.add("hidden");
    sections.classList.add("hidden");
    // parse and remove ID from courses if found
    const courseArray = JSON.parse(courses);
    const index = courseArray.indexOf(id);
    if (index > -1) {
      courseArray.splice(index, 1);
      window.localStorage.setItem(
        "coursesWithOpenSections",
        JSON.stringify(courseArray)
      );
    }
  } else {
    down.classList.add("hidden");
    up.classList.remove("hidden");
    sections.classList.remove("hidden");
    // parse and update courses with ID if found
    const courseArray = JSON.parse(courses);
    if (!courseArray.includes(id)) {
      courseArray.push(id);
      window.localStorage.setItem(
        "coursesWithOpenSections",
        JSON.stringify(courseArray)
      );
    }
  }
}

/**
 * Sets the colour of a section card based
 * on the checked form elements
 *
 * @param {number} courseID
 * @param {number} sectionNumber
 */
function updateSectionColour(courseID, sectionNumber) {
  const toDo = "bg-red-400";
  const inProgress = "bg-orange-400";
  const completed = "bg-lime-400";
  const section = document.getElementById(
    `section-${courseID}-${sectionNumber}`
  );
  if (section) {
    const cardsMade = document.getElementById(
      `course-${courseID}-section-${sectionNumber}-cards_made`
    );
    const complete = document.getElementById(
      `course-${courseID}-section-${sectionNumber}-complete`
    );
    // update the colour
    if (cardsMade.checked && complete.checked) {
      section.classList.remove(toDo);
      section.classList.remove(inProgress);
      section.classList.add(completed);
    } else if (cardsMade.checked || complete.checked) {
      section.classList.remove(toDo);
      section.classList.remove(completed);
      section.classList.add(inProgress);
    } else {
      section.classList.remove(inProgress);
      section.classList.remove(completed);
      section.classList.add(toDo);
    }
  }
}

/**
 * Displays the form allowing the user to upload
 * multiple section in JSON format
 *
 * @param {string} resourceId
 */
function displaySectionJSONForm(resourceId) {
  const form = document.getElementById(`sections-${resourceId}-import-form`);
  if (form) {
    form.classList.remove("hidden");
    // display hide form button
    const formBtn = document.getElementById(
      `sections-${resourceId}-json-close-btn`
    );
    formBtn.classList.remove("hidden");
    // create JSON sample as default value
    const textArea = document.getElementById(`sections-${resourceId}-json`);
    textArea.value = JSON.stringify(
      {
        sections: [
          { number: 1, title: "Example title" },
          { number: 2, title: "Add more as needed..." },
        ],
      },
      undefined,
      2
    );
    // hide the add section and import JSON links
    const addSectionBtn = document.getElementById(`sections-${resourceId}-btn`);
    const importJsonBtn = document.getElementById(
      `sections-${resourceId}-import-btn`
    );
    addSectionBtn.classList.add("hidden");
    importJsonBtn.classList.add("hidden");
  }
}

/**
 * Hides the form allowing the user to upload
 * multiple section in JSON format
 *
 * @param {string} resourceId
 */
function hideSectionJSONForm(resourceId) {
  const form = document.getElementById(`sections-${resourceId}-import-form`);
  if (form) {
    form.classList.add("hidden");
    const formBtn = document.getElementById(
      `sections-${resourceId}-json-close-btn`
    );
    formBtn.classList.add("hidden");
    // display the add section and import JSON links
    const addSectionBtn = document.getElementById(`sections-${resourceId}-btn`);
    const importJsonBtn = document.getElementById(
      `sections-${resourceId}-import-btn`
    );
    addSectionBtn.classList.remove("hidden");
    importJsonBtn.classList.remove("hidden");
  }
}
