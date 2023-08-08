import ldap
from django.contrib.auth.models import Group
from django_auth_ldap.backend import LDAPBackend

from helpdesk.models import Department, Employee


class CustomLDAPBackend(LDAPBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username.split("@")[0], password, **kwargs)

        if user is not None:
            if Employee.objects.filter(user=user).exists():
                return user
            # Получаем LDAP объект пользователя
            ldap_user = user.ldap_user

            # Получаем отдел из атрибута 'department'
            department = ldap_user.attrs.get('department', [None])[0]
            name = ldap_user.attrs.get('givenName', [None])[0]
            surname = ldap_user.attrs.get('sn', [None])[0]
            email = ldap_user.attrs.get('mail', [None])[0]
            ou_list = ldap_user.attrs.get('distinguishedName', [])
            user.first_name = name
            user.last_name = surname
            user.email = email
            user.save()

            target_ou = 'управление по информатизации'
            if any(target_ou.lower() in ou.lower() for ou in ou_list):

                if Department.objects.filter(name=department).exists():
                    dep = Department.objects.get(name=department)
                else:
                    dep = Department.objects.create(name=department)
                if not Employee.objects.filter(user=user).exists():
                    Employee.objects.create(user=user, department=dep)

                employee_group = Group.objects.get(name='Employee')
                user.groups.add(employee_group)
            else:
                employee_group = Group.objects.get(name='Users')
                user.groups.add(employee_group)

        return user

