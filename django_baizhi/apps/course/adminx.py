import xadmin

from course import models


class CourseCategoryModelAdmin(object):
    pass


xadmin.site.register(models.CourseCategory, CourseCategoryModelAdmin)


class CourseModelAdmin(object):
    pass


xadmin.site.register(models.Course, CourseModelAdmin)


class CourseChapterModelAdmin(object):
    pass


xadmin.site.register(models.CourseChapter, CourseChapterModelAdmin)


class CourseLessonModelAdmin(object):
    pass


xadmin.site.register(models.CourseLesson, CourseLessonModelAdmin)


class TeacherModelAdmin(object):
    pass


xadmin.site.register(models.Teacher, TeacherModelAdmin)




class CourseDiscountModelAdmin(object):
    pass


xadmin.site.register(models.CourseDiscount, CourseDiscountModelAdmin)


class ActivityModelAdmin(object):
    pass


xadmin.site.register(models.Activity, ActivityModelAdmin)


class CoursePriceDiscountModelAdmin(object):
    pass


xadmin.site.register(models.CoursePriceDiscount, CoursePriceDiscountModelAdmin)


class CourseExpireModelAdmin(object):
    pass


xadmin.site.register(models.CourseExpire, CourseExpireModelAdmin)
