# Add More Levels

![mechanics space polish and systems](https://raw.githubusercontent.com/mickfuzz/getting-started-making-a-platformer-test1/master/images/patterns/gameMechanics_more_levels.jpg)

* **Name:** Add More Levels

* **Description:** The player reaches the goal of the first Level of the platformer and then progresses to the next level (and beyond)

* **Need for Pattern:** Having more than one level is a way increasing the length and challenge of the game. You can also bring other elements
of design and even game mechanics to new levels.

* **Coding Concepts involved:** [Data](learningDimensions#data), [Variables](learningDimensions#variables),

* **Links to other Computing Patterns:** [Systems Dynamics](learningDimensionss#systems-dynamics), [Change Listener](learningDimensions#change-listener)

## Putting the Pattern into Practice

Check our code: what we need to know and do<br></h2>
<p>There is some background knowledge in this book that will be useful for us in getting this mechanic to work;</p>
<ul><li>Adding Sprites in Groups - see <a href="http://write.flossmanuals.net/learn-javascript-with-phaser/create-a-game-space/"> Create a Game Space</a></li><li>Working with Loops - see <a href="http://write.flossmanuals.net/learn-javascript-with-phaser/adding-a-reward/"> Adding a Reward</a></li><li style="">Have a good grip of how all our code fits together - see <a href="#adding-game-states">Understanding our Game Structure</a><br></li></ul>

<div></div>
<h3>Going over the code:</h3><p style="">The code for a minimal example of the code for adding levels in a simple way here- <a href="https://glitch.com/edit/#!/gamespace-more-levels-simple?path=js/game.js">https://glitch.com/edit/#!/gamespace-more-levels-simple?path=js/game.js</a><br></p><p>Note this global variable at the start of our code outside of any particular function. It is located here as it needs to be used by more than one function;</p>
<pre> var currentLevel = 1;
</pre>

<p style="">This <b>currentLevel</b> variable keeps a track of what level we are on. It is set to <b>1</b> to start off with. Now in the create function - find the section where you design your levels using grids. Copy the formatting of levels one to three, to create a new level4  variable. This will look like the code below.  <br></p>

<pre>    var level4 = [
        "                 ",
        "                 ",
        "                 ",
        "                 ",
        "                 ",
        "                 ",
        "                 ",
        "                 ",
        "                 ",
        "                 ",
        "                o",
        "xxxxxxxxxxxxxxxxx"
    ];
</pre>
<p style="">Next we also need to add another option to the section where the code finds out what level we are on and then sends that level to the loadLevel function to make the coins, platforms and enemies appear on the screen. Add this code to that section. <br></p>
<pre>  } else if (currentLevel === 4) {
    loadLevel(level4);
  }
</pre>


<p style="">We can keep adding more levels and using this way of designing them to add challenge to our game.<br></p><h3 style="">Having more control - Adding our different kinds of coins / enemies / platforms</h3><p style="">When we use the grid layout in this way there are limits in the way we use it. For example if we want to create a larger enemy than 32 pixels wide or high then we won't be able to do it well using this grid. </p><p style="">We have some options for how to overcome this limit. One way is to get rid of this grid completely and to design our levels from scratch, another is to keep the grid but also to add in our own elements to it. </p><p style="">Let's take the example of adding our own larger, or moving enemy. We can follow instructions for how to create one in this chapter - <a href="#game-mechanic-add-moving-enemies">Adding a moving enemy</a>.</p><p style="">In short we add 4 lines to our create function. If we are using our Grid Game Template, this has the side effect of making that moving enemy appear in the same place on every level. So to avoid that happening we will add the same code but we will add it only to level 1 by placing it in the following location. </p>

<pre style="">    if (!currentLevel || currentLevel === 1) {
      loadLevel(level1);
      // add extra code for just level one here<br>
      var enemy1 = game.add.sprite(370, 320, "enemy");
      enemies.add(enemy1);
      var tween1 = game.add.tween(enemy1);
      tween1.to({x:170, y: 320}, 2000, null, true, 0,-1,true);
</pre><p style="">We can see here that this will only appear on the first level. </p><p style="">We can now add our own moving enemies, or special power ups and custom size platforms, coins or hazards for each level.Have fun with this!<br></p><h3 style="">Other ideas to extend this mechanic</h3><p style="">Other ideas to extend this mechanic could include</p><ul><li style="">Adding a Game Over state - see <a href="#adding-game-states">Understanding our Game Structure</a><br></li><li style="">Loading platform and coin data more efficiently using Json - see <a href="#game-mechanic-adding-levels">Add Level Data with Json</a><br></li></ul><p>That's it. We hope you enjoy adding this game element to your game.</p>

## Test your Changes and Next Steps

Test your game to check that your changes have the desired behaviour and that there are no side effects.
For example check that each time you touch the end goal you progress by a level and the design matches.

This Game Pattern is one of many allowing you to make improvements to your platform game and to learn coding and wider computing concepts.
Find more on the [Game Pattern page](gamePatterns.md).
