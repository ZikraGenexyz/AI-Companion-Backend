from django.shortcuts import render
from companion_app import models
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view

class FriendViews:
    @staticmethod
    @api_view(['POST'])
    def get_friend_list(request):
        user_id = request.data['user_id']
        friend_list = models.Children_Accounts.objects.filter(user_id=user_id).first().friend_list

        friends = []
        pending = []
        requests = []

        for i, friend_id in enumerate(friend_list['friends']):
            user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
            friends.append({
                'id': friend_id,
                'name': user.username,
                'status': 'online'
            })

        for i, friend_id in enumerate(friend_list['pending']):
            user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
            pending.append({
                'id': friend_id,
                'name': user.username,
                'status': 'offline'
            })

        for i, friend_id in enumerate(friend_list['requests']):
            user = models.Children_Accounts.objects.filter(user_id=friend_id).first()
            requests.append({
                'id': friend_id,
                'name': user.username,
                'email': user.email,
                'status': 'offline'
            })

        return Response({
            'friends': friends,
            'pending': pending,
            'requests': requests
        }, status=HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    def accept_friend(request):
        current_user_id = request.data['user_id']
        target_user_id = request.data['target_user_id']

        current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
        target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()
        
        current_user_friends.friend_list['pending'].remove(target_user_id)
        current_user_friends.friend_list['friends'].append(target_user_id)
        current_user_friends.save()
        
        target_user_friends.friend_list['requests'].remove(current_user_id)
        target_user_friends.friend_list['friends'].append(current_user_id)
        target_user_friends.save()
        
        return Response({'message': 'Friend request accepted'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    def reject_friend(request):
        current_user_id = request.data['user_id']
        target_user_id = request.data['target_user_id']

        current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
        target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()

        current_user_friends.friend_list['pending'].remove(target_user_id)
        current_user_friends.save()

        target_user_friends.friend_list['requests'].remove(current_user_id)
        target_user_friends.save()
        
        return Response({'message': 'Friend request rejected'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    def remove_friend(request):
        current_user_id = request.data['user_id']
        target_user_id = request.data['target_user_id']
        
        # Get current user's friend list
        current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
        if not current_user_friends:
            return Response({'error': 'User not found'}, status=HTTP_400_BAD_REQUEST)
        
        # Get target user's friend list
        target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()
        if not target_user_friends:
            return Response({'error': 'Target user not found'}, status=HTTP_400_BAD_REQUEST)
        
        # Check which list to remove from
        if target_user_id in current_user_friends.friend_list['friends']:
            # Remove from friends list
            current_user_friends.friend_list['friends'].remove(target_user_id)
            current_user_friends.save()
            
            # Also remove current user from target user's friends list
            if current_user_id in target_user_friends.friend_list['friends']:
                target_user_friends.friend_list['friends'].remove(current_user_id)
                target_user_friends.save()
                
            return Response({'message': 'Friend removed successfully'}, status=HTTP_200_OK)
        
        elif target_user_id in current_user_friends.friend_list['requests']:
            # Cancel friend request
            current_user_friends.friend_list['requests'].remove(target_user_id)
            current_user_friends.save()
            
            # Remove from target user's pending list
            if current_user_id in target_user_friends.friend_list['pending']:
                target_user_friends.friend_list['pending'].remove(current_user_id)
                target_user_friends.save()
                
            return Response({'message': 'Friend request canceled'}, status=HTTP_200_OK)
        
        elif target_user_id in current_user_friends.friend_list['pending']:
            # Reject friend request
            current_user_friends.friend_list['pending'].remove(target_user_id)
            current_user_friends.save()
            
            # Remove from target user's requests list
            if current_user_id in target_user_friends.friend_list['requests']:
                target_user_friends.friend_list['requests'].remove(current_user_id)
                target_user_friends.save()
                
            return Response({'message': 'Friend request rejected'}, status=HTTP_200_OK)
        
        return Response({'message': 'User not found in any friend list'}, status=HTTP_400_BAD_REQUEST)

    @staticmethod
    @api_view(['PUT'])
    def send_friend_request(request):
        current_user_id = request.data['user_id']
        target_user_id = request.data['target_user_id']

        current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
        target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()    

        current_user_friends.friend_list['requests'].append(target_user_id)
        current_user_friends.save()

        target_user_friends.friend_list['pending'].append(current_user_id)
        target_user_friends.save()

        return Response({'message': 'Friend request sent'}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def search_user(request):
        users = models.Children_Accounts.objects.filter(username__icontains=request.data['query'])
        
        user_list = []

        for i, user in enumerate(users):
            if user.account.user_id != request.data['user_id']:
                user_list.append({
                    'id': user.account.user_id,
                    'name': user.username,
                    'email': user.email
                })

        return Response({"users": user_list}, status=HTTP_200_OK)

    @staticmethod
    @api_view(['PUT'])
    def cancel_friend_request(request):
        current_user_id = request.data['user_id']
        target_user_id = request.data['target_user_id']

        current_user_friends = models.Children_Accounts.objects.filter(user_id=current_user_id).first()
        target_user_friends = models.Children_Accounts.objects.filter(user_id=target_user_id).first()

        current_user_friends.friend_list['requests'].remove(target_user_id)
        current_user_friends.save()

        target_user_friends.friend_list['pending'].remove(current_user_id)
        target_user_friends.save()

        return Response({"message": "Friend request canceled"}, status=HTTP_200_OK)

# Legacy function-based views for backward compatibility
Get_Friend_List = FriendViews.get_friend_list
Accept_Friend = FriendViews.accept_friend
Reject_Friend = FriendViews.reject_friend
Remove_Friend = FriendViews.remove_friend
Send_Friend_Request = FriendViews.send_friend_request
Search_User = FriendViews.search_user
Cancel_Friend_Request = FriendViews.cancel_friend_request 