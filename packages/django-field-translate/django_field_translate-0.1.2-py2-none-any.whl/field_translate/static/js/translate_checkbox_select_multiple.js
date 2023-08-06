/**
 * Created by pedroreis on 12/03/18.
 */
$(function() {
    $('[data-lang]').parent().hide();
    var lang = $('#id_lang');

    if(lang.val() !== '') {
        $('[data-lang="__lang__"]'.replace('__lang__',lang.val())).parent().show();
    }

    lang.on('change',function(){
        $('[data-lang]').parent().hide();
        $('[data-lang="__lang__"]'.replace('__lang__',$(this).val())).parent().show();
    });
});