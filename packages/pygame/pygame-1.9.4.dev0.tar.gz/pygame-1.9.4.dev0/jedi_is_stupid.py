import jedi

s = '''import pygame.draw
pygame.draw.
'''
print(s)
script = jedi.Script(s, 2, len('pygame.draw.'), 'test.py')
print(', '.join(c.full_name for c in script.completions()))
print ('---')

s = '''import pygame
pygame.Surface.
'''
print(s)
script = jedi.Script(s, 2, len('pygame.Surface.'), 'test.py')
print(', '.join(c.full_name for c in script.completions()))
print ('---')




s = '''import pygame
pygame.
'''
print(s)
script = jedi.Script(s, 2, len('pygame.'), 'test.py')
print(', '.join(c.full_name for c in script.completions()))
print ('---')


s = '''import pygame
pygame.transform.threshold
'''
print(s)
script = jedi.Script(s, 2, len('pygame.transform.threshold'), 'test.py')
print(', '.join(c.full_name for c in script.completions()))
print ('---')
