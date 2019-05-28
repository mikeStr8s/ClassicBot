$.get('README.md', (data) => {
    add_readme_data(data);
});

function add_readme_data(readme_string) {
    let converter = new showdown.Converter(),
        html = converter.makeHtml(readme_string);

    $('#mid').html(html);
}