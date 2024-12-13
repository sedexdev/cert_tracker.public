(function () {
  const msgContainer = document.getElementById("msg-container");
  if (msgContainer) {
    const childrenLength = msgContainer.children.length;
    if (childrenLength < 2) {
      setInterval(() => {
        msgContainer.remove();
      }, 4000);
    }
  }
})();
