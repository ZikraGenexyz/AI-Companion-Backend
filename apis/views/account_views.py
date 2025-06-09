from django.shortcuts import render
from companion_app import models
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.decorators import api_view
import random
import string
from datetime import datetime
import json

class ParentAccountViews:
    @staticmethod
    @api_view(['PUT'])
    def account_init(request):
        account_id = request.data['account_id']
        email = request.data['email']
        username = request.data['username']

        if models.Parents_Accounts.objects.filter(account_id=account_id).first() is None:
            models.Parents_Accounts.objects.create(account_id=account_id, 
                                                email=email, 
                                                username=username, 
                                                date_of_birth=None, 
                                                phone_number=None, 
                                                relation=None)

        return Response({'message': 'Account initialized successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    def account_update(request):
        account_id = request.data['account_id']
        username = request.data['username']
        date_of_birth = request.data['date_of_birth']
        phone_number = request.data['phone_number']
        relation = request.data['relation']

        models.Parents_Accounts.objects.filter(account_id=account_id).update(
            username=username, 
            date_of_birth=date_of_birth if date_of_birth != '' else None, 
            phone_number=phone_number if phone_number != '' else None, 
            relation=relation if relation != '' else None)

        return Response({'message': 'Account updated successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['GET'])
    def account_get_info(request):
        account_id = request.GET.get('account_id')
        account = models.Parents_Accounts.objects.filter(account_id=account_id).first()

        return Response({
            'username': account.username, 
            'date_of_birth': account.date_of_birth, 
            'phone_number': account.phone_number, 
            'relation': account.relation
        }, status=HTTP_200_OK)

    @staticmethod
    @api_view(['DELETE'])
    def account_delete(request):
        account_id = request.data['account_id']
        models.Parents_Accounts.objects.filter(account_id=account_id).delete()

        return Response({'message': 'Account deleted successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def get_account_users(request):
        account_id = request.data['account_id']
        users = models.Children_Accounts.objects.filter(account=models.Parents_Accounts.objects.filter(account_id=account_id).first())

        user_list = []

        for user in users:
            user_list.append({
                'id': user.user_id,
                'name': user.username
            })

        return Response({"users": user_list}, status=HTTP_200_OK)


class ChildAccountViews:
    @staticmethod
    @api_view(['POST'])
    def child_init(request):
        username = request.data['username']
        robot_type = request.data['robot_type']
        robot_color = request.data['robot_color']
        isActive = True
        user_id = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=28))
        birth_date = str(datetime.now().year - int(request.data['age'])) + '-01-01'

        models.Children_Accounts.objects.create(account=None, user_id=user_id, isActive=isActive, user_info={
            "name": username,
            "gender": "",
            "birth_date": birth_date,
            "school": "",
            "energy_level": 0,
            "robot_type": robot_type,
            "robot_color": robot_color,
        })

        return Response({'message': 'Child initialized successfully', 'user_id': user_id}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def child_bind_status(request):
        user_id = request.data['user_id']
        child = models.Children_Accounts.objects.filter(user_id=user_id).first()

        bind_status = False

        if child.account is not None:
            bind_status = True

        return Response({'bind_status': bind_status}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def get_children(request):
        users = models.Children_Accounts.objects.filter(account=models.Parents_Accounts.objects.filter(account_id=request.data['account_id']).first())
        user_list = []

        for user in users:
            completed_notes = sum(1 for note in user.notification['love_notes'] if note.get('completed', False))
            completed_missions = sum(1 for mission in user.notification['missions'] if mission.get('completed', False))

            user_list.append({
            'id': user.user_id,
            'user_info': user.user_info,
            'missions': {'completed': completed_missions, 'total': len(user.notification['missions'])},
            'loveNotes': {'completed': completed_notes, 'total': len(user.notification['love_notes'])},
            })

        return Response({'children': user_list}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def edit_child(request):
        user_id = request.data['user_id']
        username = request.data['username']
        gender = request.data['gender']
        birth_date = request.data['birth_date']
        school = request.data['school']
        robot_type = request.data['robot_type']
        robot_color = request.data['robot_color']

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()

        username = username if len(username) > 0 else child.user_info['name']
        gender = gender if len(gender) > 0 else child.user_info['gender']
        birth_date = birth_date.replace(' 00:00:00.000', '') if len(birth_date) > 0 else child.user_info['birth_date']
        school = school if len(school) > 0 else child.user_info['school']
        robot_type = robot_type if len(robot_type) > 0 else child.user_info['robot_type']
        robot_color = robot_color if len(robot_color) > 0 else child.user_info['robot_color']

        child.user_info = {
            "name": username,
            "gender": gender,
            "birth_date": birth_date,
            "school": school,
            "energy_level": child.user_info['energy_level'],
            "robot_type": robot_type,
            "robot_color": robot_color,
        }
        child.save()

        return Response({'message': 'Child updated successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def get_child_info(request):
        user_id = request.data['user_id']
        child = models.Children_Accounts.objects.filter(user_id=user_id).first()

        mission_list = child.notification['missions']
        love_note_list = child.notification['love_notes']
        user_info = child.user_info

        return Response({
            'missions': mission_list, 
            'love_notes': love_note_list, 
            'user_info': user_info}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def add_user(request):
        account_id = request.data['account_id']
        username = request.data['username']
        user_id = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=28))

        models.Children_Accounts.objects.create(account=models.Parents_Accounts.objects.filter(account_id=account_id).first(), user_id=user_id, username=username)

        return Response({'message': 'User initialized successfully', 'user_id': user_id}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['DELETE'])
    def remove_user(request):
        user_id = request.data['user_id']
        models.Children_Accounts.objects.filter(user_id=user_id).delete()

        return Response({'message': 'User removed successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    def update_user(request):
        user_id = request.data['user_id']
        username = request.data['username']

        user = models.Children_Accounts.objects.filter(user_id=user_id).first()
        user.username = username
        user.save()

        return Response({'message': 'User updated successfully'}, status=HTTP_200_OK)


class BindingViews:
    @staticmethod
    @api_view(['POST'])
    def create_bind_otp(request):
        user_id = request.data['user_id']
        otp = ''.join(random.choices(string.digits, k=4))

        child = models.Children_Accounts.objects.filter(user_id=user_id).first()
        child.bind_otp = otp
        child.save()

        return Response({'message': 'Bind OTP created successfully', 'otp': otp}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def verify_bind_otp(request):
        account_id = request.data['account_id']
        otp = request.data['otp']

        user = models.Children_Accounts.objects.filter(bind_otp=otp).first()

        if user is not None:
            user.bind_otp = None
            user.account = models.Parents_Accounts.objects.filter(account_id=account_id).first()
            user.save()

            return Response({'message': 'Bind OTP verified successfully'}, status=HTTP_200_OK)
        else:
            return Response({'message': 'Bind OTP verification failed'}, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    @api_view(['POST'])
    def unbind_children_account(request):
        user_id = request.data['user_id']

        user = models.Children_Accounts.objects.filter(user_id=user_id).first()
        user.account = None
        user.save()

        return Response({'message': 'Account unbound successfully'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def bind_children_account(request):
        user_id = request.data['user_id']
        account_id = request.data['account_id']

        user = models.Children_Accounts.objects.filter(user_id=user_id).first()
        user.account = models.Parents_Accounts.objects.filter(account_id=account_id).first()
        user.save()

        return Response({'message': 'Account bound successfully'}, status=HTTP_200_OK)


# Legacy function-based views for backward compatibility
Account_Init = ParentAccountViews.account_init
Account_Update = ParentAccountViews.account_update
Account_Get_Info = ParentAccountViews.account_get_info
Account_Delete = ParentAccountViews.account_delete
Get_Account_Users = ParentAccountViews.get_account_users

Child_Init = ChildAccountViews.child_init
Child_Bind_Status = ChildAccountViews.child_bind_status
Get_Children = ChildAccountViews.get_children
Edit_Child = ChildAccountViews.edit_child
Get_Child_Info = ChildAccountViews.get_child_info
Add_User = ChildAccountViews.add_user
Remove_User = ChildAccountViews.remove_user
Update_User = ChildAccountViews.update_user

Create_Bind_OTP = BindingViews.create_bind_otp
Verify_Bind_OTP = BindingViews.verify_bind_otp
Unbind_Children_Account = BindingViews.unbind_children_account
Bind_Children_Account = BindingViews.bind_children_account 