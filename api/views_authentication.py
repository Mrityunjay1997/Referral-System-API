from accounts.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout,login
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from api.serializer import UserSerializer
from django.core.paginator import Paginator
import random


def GetPagesData(page, data):
	if page:
		if str(page) == '1':
			start = 0
			end = start + 20
		else:
			start = 20 * (int(page)-1)
			end = start + 20
	else:
		start = 0
		end = start + 20
	page_data_value = Paginator(data, 20)	
	last_page = True if page_data_value.num_pages == int(page if page else 1) else False
	try:
		total_results = data.count() if data else 0
	except:
		total_results = len(data)
	meta_data = { 
		"page_count": page_data_value.num_pages,
		"total_results": total_results,
		"current_page_no": int(page if page else 1),
		"limit": 20,
		"last_page": last_page
	}
	return start,end,meta_data



def UserAuthenticate(email, password):
    user = User.objects.filter(email=email).order_by('created_on').last()
    if user.check_password(password):
        return user
    else:
        return None
  

def GenerateReferralCode():
    code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for i in range(0, 10):
        slice_start = random.randint(0, len(code_chars) - 1)
        code += code_chars[slice_start: slice_start + 1]  
    return code


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="Login",
        operation_description="Login",
        request_body = openapi.Schema(
            type = openapi.TYPE_OBJECT,
            required = ['email','password'],
            properties = {
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        if not request.data.get("email"):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("password"):
            return Response({"message":"Please enter password"},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserAuthenticate(
                email = request.data.get("email"), 
                password = request.data.get("password"),
            )
        except:
            return Response({"message":"Invalid Login Credentials.", "status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response({"message":"Invalid Login Credentials.", "status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            
        message = "Login Successfully"
        login(request, user)
        user.save()
        Token.objects.filter(user = user).delete()
        token = Token.objects.create(user = user)
        data = UserSerializer(user,context = {"request":request}).data
        data.update({"token":token.key})   
        return Response({"message":message,"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class SignupCustomerView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="Signup ",
        operation_description="Signup",
        request_body = openapi.Schema(
            type = openapi.TYPE_OBJECT,
            required = ['full_name','email','password'],
            properties = {
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                
            }
        )
    )
    def post(self, request, *args, **kwargs):
        if not request.data.get("full_name"):
            return Response({"message":"Please enter full name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if not request.data.get("email"):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("password"):
            return Response({"message":"Please enter password","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=request.data.get("email")):
            return Response({"message":"There is already a registered user with this email id.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)


        if request.data.get('referral_code'):
            referrer = User.objects.filter(referral_code=request.data.get('referral_code')).last()
            if not referrer:
                return Response({"message":"Invalid Referral Code"},status=status.HTTP_400_BAD_REQUEST)
        else:
            referrer = None
        user = User.objects.create(
            full_name = request.data.get("full_name"),
            email = request.data.get("email"),
            password = make_password(request.data.get("password")),
            referral_code = GenerateReferralCode(),
            is_profile_verified = True,
        )
        
        Token.objects.filter(user = user).delete()
        token = Token.objects.create(user = user)      
        data = UserSerializer(user,context = {"request":request}).data
        data.update({"token":token.key}) 
        return Response({"message":"User Registered Successfully!","data":data},status=status.HTTP_200_OK)



       

class LogoutView(APIView): 
    permission_classes = (permissions.IsAuthenticated,) 

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="Logout",
        operation_description="Logout",
    )
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)  
        Token.objects.filter(user=user).delete()
        logout(request)       
        return Response({"message":"Logout Successfully!","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)



class GetProfileDetails(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        tags=["User Profile"],
        operation_id="Profile Details",
        operation_description="Profile Details",
    )
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User matching query doesnot exist.","status":status.HTTP_400_BAD_REQUEST}) 
        data = UserSerializer(user,context = {"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)




class GetRefereedUserList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        tags=["Refered User List"],
        operation_id="Referred User List",
        operation_description="Referres User List",
        manual_parameters=[openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_STRING)],
    )
    def get(self, request, *args, **kwargs):
        user = User.objects.filter(referred_by=request.user,is_referred=True)
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, user.order_by('-created_on'))
        data = UserSerializer(user.order_by('-created_on')[start : end],many=True,context={"request":request}).data
        return Response({"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
