str = "*whirrs and beeps* Ah, just a friendly hello in return! It's great to have you here. How's everything going, or should I ask again?"

str = ' '.join(str.split('*')[::2])

print(str)