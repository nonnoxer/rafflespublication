//var Size = Quill.import('attributors/style/size');
//Quill.register(Size, true);


var quill = new Quill('#editor-container', {
  modules: {
    toolbar: [
      [{ 'header': [1, 2, 3, false, 5, 6,] }, { 'font': [] }, { 'size' : [ 'small', false, 'large', 'huge' ] }],
      //[{ 'font': [] }, { 'size': ['10px', '20px', '80px'] }],
      ['bold', 'italic', 'underline', 'strike', { 'color': [] }, { 'background': [] }],
      [{ 'script': 'super' }, { 'script': 'sub' }, 'blockquote', 'code-block'],
      ['link', 'image'],
      [{ 'align': [] }],
      [{ 'list': 'ordered' }, { 'list': 'bullet'}, { 'indent': '-1' }, { 'indent': '+1' }]
    ]
  },
  placeholder: 'Start writing...',
  theme: 'snow'
});

var previewer =  new Quill('#preview', {
  theme: 'bubble',
  modules: {
      toolbar: false,
  },
  readOnly: true,
});

function dewit() {
  form = document.getElementById('editor');
  $("textarea[name='text']").html(JSON.stringify(quill.getContents()));
  form.submit();
}
function lne() {
  lestring = document.getElementById('text').textContent;
  var mydelta = JSON.parse(lestring);
  var deltaOps =  mydelta["ops"];
  quill.setContents(deltaOps);
}
function ean() {
  $('#titlep').text($('#title').val());
  $('#catep').text($('#cate').val());
  previewer.setContents(quill.getContents());
}

$('#myfile').on('change',function(){
  //get the file name
  var fileName = $(this).val();
  //replace the "Choose a file" label
  $(this).next('.custom-file-label').html(fileName);
})