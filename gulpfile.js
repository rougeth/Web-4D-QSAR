var gulp = require('gulp'),
    bower = require('gulp-bower'),
    sass = require('gulp-sass');

var config = {
    bowerDir: './bower_components',
    bootstrapDir: './bower_components/bootstrap-sass',
}

gulp.task('bower', function() {
    return bower()
        .pipe(gulp.dest(config.bowerDir));
});

gulp.task('style-css', function() {
    return gulp.src('./src/static/css/base.scss')
        .pipe(sass({
            includePaths: [config.bootstrapDir + 'assets/stylesheets']
        }))
        .pipe(gulp.dest('./src/static/css'));
});

gulp.task('default', ['style-css']);

gulp.task('watch', function() {
    gulp.watch('./src/static/css/base.scss', ['default']);
});
