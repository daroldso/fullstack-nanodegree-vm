from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Genre, Base, Artist, User

from datetime import datetime

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

User1 = User(name="Darold So", email="daroldso@example.com",
             picture='https://avatars0.githubusercontent.com/u/9425789?v=3&s=460')
session.add(User1)
session.commit()

genre1 = Genre(name="Rock", user=User1)
session.add(genre1)
session.commit()

artist1 = Artist(name="Guns N' Roses", biography="""At a time when pop was dominated by dance music and pop-metal, Guns N' Roses brought raw, ugly rock & roll crashing back into the charts. They were not nice boys; nice boys don't play rock & roll. They were ugly, misogynistic, and violent; they were also funny, vulnerable, and occasionally sensitive, as their breakthrough hit, \"Sweet Child O' Mine,\" showed. While Slash and Izzy Stradlin ferociously spit out dueling guitar riffs worthy of Aerosmith or the Stones, Axl Rose screeched out his tales of sex, drugs, and apathy in the big city. Meanwhile, bassist Duff McKagan and drummer Steven Adler were a limber rhythm section who kept the music loose and powerful.
    Guns N' Roses' music was basic and gritty, with a solid hard, bluesy base; they were dark, sleazy, dirty, and honest -- everything that good hard rock and heavy metal should be. There was something refreshing about a band that could provoke everything from devotion to hatred, especially since both sides were equally right. There hadn't been a hard rock band this raw or talented in years, and they were given added weight by Rose's primal rage, the sound of confused, frustrated white trash vying for a piece of the pie. As the '80s became the '90s, there simply wasn't a more interesting band around, but owing to intra-band friction and the emergence of alternative rock, Rose's supporting cast eventually left, and he spent over 15 years recording before the long-delayed Chinese Democracy appeared in 2008.""", created_at=datetime.today(), genre=genre1, user=User1)
session.add(artist1)
session.commit()

artist2 = Artist(name="Linkin Park", biography="""Although rooted in alternative metal, Linkin Park became one of the most successful acts of the 2000s by welcoming elements of hip-hop, modern rock, and atmospheric electronica into their music. The band's rise was indebted to the aggressive rap-rock movement made popular by the likes of Korn and Limp Bizkit, a movement that paired grunge's alienation with a bold, buzzing soundtrack.
    Linkin Park added a unique spin to that formula, however, focusing as much on the vocal interplay between singer Chester Bennington and rapper Mike Shinoda as the band's muscled instrumentation, which layered DJ effects atop heavy, processed guitars. While the group's sales never eclipsed those of its tremendously successful debut, Hybrid Theory, few alt-metal bands rivaled Linkin Park during the band's heyday.""", created_at=datetime.today(), genre=genre1, user=User1)
session.add(artist2)
session.commit()

genre2 = Genre(name="Funk Rock", user=User1)
session.add(genre2)
session.commit()

artist3 = Artist(name="Red Hot Chili Peppers", biography="""Few rock groups of the '80s broke down as many musical barriers and were as original as the Red Hot Chili Peppers. Creating an intoxicating new musical style by combining funk and punk rock together (with an explosive stage show to boot), the Chili Peppers spawned a slew of imitators in their wake, but still managed to be the leaders of the pack by the dawn of the 21st century. The roots of the band lay in a friendship forged by three school chums, Anthony Kiedis, Michael Balzary, and Hillel Slovak, while they attended Fairfax High School in California back in the late '70s/early '80s. While Balzary and Slovak showed great musical promise (on trumpet and guitar, respectively), Kiedis focused on poetry and acting during his high-school career. During this time, Slovak taught Balzary how to play bass, while the duo encouraged Kiedis to start putting his poetry to music, which he soon did.
    Influenced heavily by the burgeoning L.A. punk scene (the Germs, Black Flag, Fear, Minutemen, X, etc.) as well as funk (Parliament-Funkadelic, Sly & the Family Stone, etc.), the trio began to rehearse with another friend, drummer Jack Irons, leading to the formation of Tony Flow & the Miraculously Majestic Masters of Mayhem, a quartet that played strip bars along the Sunset Strip during the early '80s. It was during this time that the four honed their sound and live act (as they stumbled across a stage gimmick that would soon become their trademark -- performing on-stage completely naked, except for a tube sock covering a certain part of their anatomy). By 1983, Balzary had begun to go by the name \"Flea,\" and the group changed its name to the Red Hot Chili Peppers.""", created_at=datetime.today(), genre=genre2, user=User1)
session.add(artist3)
session.commit()

print "added user, genre and artist!"
