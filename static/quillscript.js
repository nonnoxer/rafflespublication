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
  placeholder: 'Start writing...',
  theme: 'snow'  // or 'bubble'
});
function dewit() {
  form = document.getElementById('editor');
  //$("textarea[name='text']").html(quill.root.innerHTML);

  $("textarea[name='text']").html(JSON.stringify(quill.getContents()));

  form.submit();
}
function lne() {
  lestring = document.getElementById('text').textContent;
  var mydelta = JSON.parse(lestring);
  var deltaOps =  mydelta["ops"];  
  quill.setContents(deltaOps);
  //quill.root.innerHTML = document.getElementById('text').value;
}