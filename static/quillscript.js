var quill = new Quill('#editor-container', {
  modules: {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }, { 'font': [] }, { 'size' : [ 'small', false, 'large', 'huge' ] }],
      ['bold', 'italic', 'underline', 'strike', { 'color': [] }, { 'background': [] }],
      [{ 'script': 'super' }, { 'script': 'sub' }, 'blockquote', 'code-block'],
      ['link', 'image'],
      [{ 'align': [] }],
      [{ 'list': 'ordered' }, { 'list': 'bullet'}, { 'indent': '-1' }, { 'indent': '+1' }]
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
lne = () => quill.root.innerHTML = document.getElementById('text').value;
