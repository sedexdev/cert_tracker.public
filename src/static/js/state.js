(function () {
  window.onload = () => {
    // update the state if the path is whitelisted
    if (window.location.pathname.includes("/certs/data")) {
      console.log("Updating state...");
      if (window.localStorage.getItem("currentNav")) {
        setCurrentNav(window.localStorage.getItem("currentNav"));
        setDisplayedContent(window.localStorage.getItem("currentNav"));
        setDisplayAddContentBtn(window.localStorage.getItem("currentNav"));
        setExpandedSections();
        setResourceFormState();
      } else {
        const nav = document.getElementById("nav-statistics");
        nav.classList.add("selected");
        const content = document.getElementById("statistics");
        content.classList.remove("hidden");
      }
      setSectionColours();
    } else {
      // clear local storage but keep dark mode if it's on
      Object.keys(localStorage).forEach((key) => {
        if (key != "darkMode") {
          window.localStorage.removeItem(key);
        }
      });
    }
  };
})();

/**
 * Sets both the nav bar and the select
 * menu on smaller screens to the last
 * selected tab
 *
 * @param {string} value
 */
function setCurrentNav(value) {
  // remove selected class from all nav elements
  const nav = document.getElementById("cert-nav");
  if (nav) {
    const links = nav.children;
    for (let link of links) {
      if (link.classList.contains("selected")) {
        link.classList.remove("selected");
      }
    }
    // update from local storage if it exists
    if (value) {
      // add selected to current nav
      const current = document.getElementById(`nav-${value}`);
      current.classList.add("selected");
      // do the same for the select menu
      const select_list = document.getElementById("content");
      select_list.value = value;
    }
  }
}

/**
 * Updates the displayed content
 *
 * @param {number} id element to update
 */
function setDisplayedContent(id) {
  const content = [
    "statistics",
    "courses",
    "videos",
    "articles",
    "documentation",
  ];
  const nav = document.getElementById("cert-nav");
  if (nav) {
    for (let topic of content) {
      const contentEl = document.getElementById(topic);
      contentEl.classList.add("hidden");
    }
    const el = document.getElementById(id);
    el.classList.remove("hidden");
  }
}

/**
 * Updates the add content buttons displayed
 *
 * @param {number} id element to update
 */
function setDisplayAddContentBtn(id) {
  const addBtn = document.getElementById("content-btn");
  const importBtn = document.getElementById("import-btn");
  if (addBtn && importBtn) {
    if (id != "statistics") {
      addBtn.classList.remove("hidden");
      importBtn.classList.remove("hidden");
    }
  }
}

/**
 * Sets the correct colours for each
 * course section
 */
function setSectionColours() {
  const sectionsRegex = /^section-(\d+)-(\d+)$/;
  const dom = document.querySelectorAll("*");
  const sections = Array.from(dom).filter((el) => sectionsRegex.test(el.id));
  const toDo = "bg-red-400";
  const inProgress = "bg-orange-400";
  const completed = "bg-lime-400";
  if (sections) {
    for (let section of sections) {
      const courseID = section.id.split("-")[1];
      const sectionNumber = section.id.split("-")[2];
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
}

/**
 * Expands already open sections that have just
 * had a new section added to them
 */
function setExpandedSections() {
  const courses = window.localStorage.getItem("coursesWithOpenSections");
  if (courses) {
    const courseArray = JSON.parse(courses);
    for (let id of courseArray) {
      const down = document.getElementById(`down-arrow-${id}`);
      const up = document.getElementById(`up-arrow-${id}`);
      const el = document.getElementById(`sections-${id}`);
      if (el) {
        down.classList.add("hidden");
        up.classList.remove("hidden");
        el.classList.remove("hidden");
      }
    }
  }
}

/**
 * Opens the resource form again after a page
 * reload in the event that an Open Graph protocol
 * hit caused a reload
 */
function setResourceFormState() {
  const show = window.localStorage.getItem("loadResourceForm");
  if (show == "true") {
    const form = document.getElementById("resource-form");
    if (form) {
      form.classList.remove("hidden");
      // hide add content buttons
      const addBtn = document.getElementById("content-btn");
      const importBtn = document.getElementById("import-btn");
      addBtn.classList.add("hidden");
      importBtn.classList.add("hidden");
      // hide tab contents
      const courses = document.getElementById("courses");
      const videos = document.getElementById("videos");
      const articles = document.getElementById("articles");
      const documents = document.getElementById("documentation");
      const content = [courses, videos, articles, documents];
      for (let topic of content) {
        topic.classList.add("hidden");
      }
    }
  } else {
    const form = document.getElementById("resource-form");
    if (form) {
      form.classList.add("hidden");
    }
    window.localStorage.removeItem("loadResourceForm");
  }
}
