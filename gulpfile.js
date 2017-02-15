/**
 * Created by thoba on 2017/02/03.
 */
//requirements
var gulp = require('gulp'),
    gulpBrowser = require('gulp-browser'),
    reactify = require('reactify'),
    del = require('del'),
    size = require('gulp-size'),
    livereload = require('gulp-livereload');

let transforms = [
    {
        transform: "babelify",
        options: {presets: ["es2015", "react"]}
    }
];
//tasks
gulp.task('transform', function () {
    return gulp.src('./combatwebapp/static/scripts/*.jsx')
        .pipe(gulpBrowser.browserify(transforms))
        .pipe(gulp.dest('./combatwebapp/static/scripts/js/'))
        .pipe(size())
        .pipe(livereload());
});

gulp.task('del', function () {
    return del(['./combatwebapp/static/scripts/js'])
});

gulp.task('default', ['del'], function () {
    gulp.start('transform');
    livereload.listen();
    gulp.watch('./combatwebapp/static/scripts/*.jsx', ['transform']);
});