import json
import requests
from pprint import pprint
import numpy as np
import random
import re
import gensim
import pyastar

from PIL import Image


def path_finder(img, food, aisles):
    depts = []
    for item in food:
        depts.append(ncr_get(item))
    pix = np.array(img)
    grid_size = pix.shape[:2]
    grid = np.ones(grid_size, dtype=np.float32)
    maze = np.ones((grid_size[0], grid_size[1], 3), dtype=np.float32)

    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            if sum(pix[i][j]) != 0:
                grid[i][j] = np.inf
                maze[i][j] = (0, 0, 0)

    assert grid.min() == 1, 'cost of moving must be at least 1'
    output = {'shelves': maze.tolist()
              , 'size': grid_size}

    # start is the first white block in the top row
    start_j, = np.where(grid[-1, :] == 1)
    start = tuple(np.array([0, start_j[0]]))

    # end is the first white block in the final column
    ends = []
    #  if isinstance(food, str):
    #      ends.append(aisles[food])
    #  elif isinstance(food, list):
    for item in depts:
        #  item_name = item.lower()
        #  if item_name not in list(aisles.keys()):
        #      raise ValueError('Unsupported food item, supported foods are %s'
        #                       % ', '.join(aisles.keys()))
        #  else:
        try:
            ends.append((grid_size[0] - aisles[item]["vertical_position"],
                         grid_size[1] - aisles[item]["horizontal_position"]
                         ))
        except KeyError:
            continue

    def find_closest(point, ends):
        shortest_dist = float('inf')
        for end in ends:
            dist = np.linalg.norm(np.array(end) - np.array(point))
            if dist == 0:
                continue
            else:
                if dist < shortest_dist:
                    shortest_dist = dist
                    closest_point = end
        return closest_point

    order = {}
    ends_scrap = [start, *ends.copy()]
    end = start
    for i in range(len(ends_scrap) - 1):
        closest = find_closest(end, ends_scrap)
        ends_scrap.remove(end)
        order[end] = closest
        end = closest

    # set allow_diagonal=True to enable 8-connectivity
    path_color = (1, 1, 0)
    for end in ends:
        #  food_item = [key for key, value in locs.items() if value == end][0]
        path = pyastar.astar_path(grid, start, end, allow_diagonal=False)
        start = end
        output['path'] = path.tolist()

        if path.shape[0] > 0:
            maze[path[:, 0], path[:, 1]] = maze[path[:, 0], path[:, 1]] - path_color
            #  print('plotting path to %s' % (food_item))
        else:
            pass
            #  print('no path found')
        path_color = (random.uniform(0.1, 0.5),
                      random.uniform(0.1, 0.3),
                      random.uniform(0.1, 0.5)
                      )
        maze_out = np.repeat(maze, 20, axis=0)
        maze_out = np.repeat(maze_out, 20, axis=1)
        maze_out = np.flipud(maze_out)

    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            maze[i, j] = maze[i, j] * 255
    output['map'] = maze.tolist()
    #  img = Image.fromarray(maze.astype('uint8'))
    #  img.show()
    return output


def ncr_get(food_item):
    """TODO: Docstring for ncr_get.

    :food_item: TODO
    :returns: TODO

    """
    product_name = food_item.replace(' ', '-')[:40]
    product_name = re.sub(r'[^\w\s]', '', product_name)

    #  print((dept_name, product_name))
    url = "https://gateway-staging.ncrcloud.com/catalog/items?itemCodePattern=%s" % product_name

    user = "acct:groceryfinder2-stg@groceryfinder2serviceuser"
    app_key = "8a0084a165d712fd0165e0b07e830012"
    pwd = 'master13'  # Use password you provided when you created your NCR profile

    headers = {'Accept': "application/json",
               'Content-Type': "application/json",
               'nep-service-version': "2.2.1:2",
               'nep-application-key': app_key
               }

    res = requests.get(url, headers=headers, auth=(user, pwd))
    try:
        return json.loads(res.text)['pageContent'][0]['departmentId']
    except (KeyError, IndexError):
        print(product_name)
        pprint(json.loads(res.text))
        return


def get_map(shopping_list):
    """TODO: Docstring for get_map.

    :shopping_list: TODO
    :returns: TODO

    """
    output = {}
    # Add locations of each item
    with open('aisle.json', 'r') as f:
        output['aisles'] = json.loads(f.read())
    im = Image.open("example.png")
    output['path'] = path_finder(im, shopping_list, output['aisles'])
    output['recommended_items'] = suggest_items(shopping_list, 3)
    print(output['recommended_items'])

    return output


def suggest_items(items, n):
    model = gensim.models.FastText.load('fasttext.model')
    return model.wv.most_similar(positive=items, topn=n)


def handler(request):
    request_json = request.get_json()
    print(request_json)
    if request_json and 'shopping_list' in request_json:
        shopping_list = request_json['shopping_list']
        return(json.dumps(get_map(shopping_list)))
    else:
        return("List not found")


#  print(handler({'shopping_list': ['Chocolate Sandwich Cookies', 'Smorz Cereal', 'Coconut Chocolate Chip Energy Bar', 'Nacho Cheese White Bean Chips', "Cut Russet Potatoes Steam N' Mash"]}))
