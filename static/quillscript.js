var quill = new Quill('#editor-container', {
  modules: {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      ['bold', 'italic', 'underline']
    ]
  },
  placeholder: 'Compose an epic...',
  theme: 'snow'  // or 'bubble'
});
function dewit() {
  form = document.getElementById('editor');
  $("textarea[name='text']").html(quill.root.innerHTML);
  form.submit();
}
function recall(lne) {
  quill.setContents(convertHtmlToDelta(lne));
}
