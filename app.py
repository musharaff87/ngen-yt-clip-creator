from gemini_api import get_brief_content

if __name__ == "__main__":
    # Example sentences
    sentence = "peacock is the beautiful bird"
    sample_content_1 = """ Did you know that parrots are some of the most intelligent birds on the planet? Seriously, they're like the Einstein's of the bird world! But let's talk about them in a little more detail.

Parrots are a diverse group of birds, with over 350 species found all over the world. They're known for their bright colors, their ability to mimic sounds (including human speech!), and their complex social structures.  These guys are super social, living in flocks and communicating with each other using a variety of calls and whistles. It's like their own little bird language!

Their beaks are powerful tools, helping them crack open nuts and seeds (non-living objects!), and even shred their food. Some species, like the Amazon parrots, are known for their incredible ability to mimic sounds. They can learn words, phrases, and even entire songs! This is because they have a special structure in their vocal cords called a syrinx, which allows them to produce a wide range of sounds.

Parrots have evolved to live in a variety of habitats, from lush rainforests to dry grasslands. They often build their nests in tree cavities (non-living objects!), using sticks, leaves, and even feathers for bedding.  They play a vital role in their ecosystems, helping to disperse seeds and control insect populations.

So next time you see a parrot, remember that these amazing creatures are more than just pretty faces. They're intelligent, social, and vital members of the natural world! """

    #brief_content = get_brief_content(sentence)
    brief_content = sample_content_1
    print(f"Brief for '{sentence}':\n{brief_content}\n")

