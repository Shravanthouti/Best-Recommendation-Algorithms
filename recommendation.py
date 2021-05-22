import operator
import networkx as nx
import matplotlib.pyplot as plt
import random
import sys


def create_romeojuliet_graph():
    rj = nx.Graph()
    rj.add_node("Tybalt")
    rj.add_node("Nurse")
    rj.add_node("Juliet")
    rj.add_node("Friar Laurence")
    rj.add_node("Capulet")
    rj.add_node("Benvolio")
    rj.add_node("Romeo")
    rj.add_node("Mercutio")
    rj.add_node("Montague")
    rj.add_node("Paris")
    rj.add_node("Escalus")

    rj.add_edge("Juliet", "Tybalt")
    rj.add_edge("Nurse", "Juliet")
    rj.add_edge("Juliet", "Capulet")
    rj.add_edge("Juliet", "Romeo")
    rj.add_edge("Juliet", "Friar Laurence")
    rj.add_edge("Tybalt", "Capulet")
    rj.add_edge("Romeo", "Benvolio")
    rj.add_edge("Romeo", "Friar Laurence")
    rj.add_edge("Romeo", "Mercutio")
    rj.add_edge("Romeo", "Montague")
    rj.add_edge("Benvolio", "Montague")
    rj.add_edge("Mercutio", "Escalus")
    rj.add_edge("Montague", "Escalus")
    rj.add_edge("Paris", "Mercutio")
    rj.add_edge("Escalus", "Paris")
    rj.add_edge("Capulet", "Paris")
    rj.add_edge("Capulet", "Escalus")

    return rj


def friends(graph, user):
    return set(graph.neighbors(user))


def friends_of_friends(graph, user):
    userfriends = friends(graph, user)
    finalfriends = set()
    for names in userfriends:
        friends_of_userfriends = friends(graph, names)
        for names2 in friends_of_userfriends:
            if(names2 not in userfriends and names2 != user):
                finalfriends.add(names2)
    return finalfriends


def common_friends(graph, user1, user2):
    user1friends = friends(graph, user1)
    user2friends = friends(graph, user2)
    commonfriends = user1friends.intersection(user2friends)
    return commonfriends


def number_of_common_friends_map(graph, user):
    all_names = set(graph.nodes())
    all_names.remove(user)
    users_friends = friends(graph, user)
    friend_map = {}
    for names in all_names:
        temp_friends = common_friends(graph, user, names)
        num_friends = len(temp_friends)
        if num_friends > 0 and names not in users_friends:
            friend_map[names] = num_friends
    return friend_map


def number_map_sorted_list(friendmap):
    temp_list = sorted(friendmap.items(),
                       key=operator.itemgetter(1), reverse=True)
    friend_list = [items[0] for items in temp_list]
    return friend_list


def recommend_by_number_of_common_friends(graph, user):
    friendmap = number_of_common_friends_map(graph, user)
    friend_recommend = number_map_sorted_list(friendmap)
    return friend_recommend


def create_facebook_graph(file_path):
    fb_file = open(file_path, "r")
    fb_data_list = fb_file.readlines()
    fb_graph = nx.Graph()

    for data in fb_data_list:
        friend_list = data.split()
        friend_one = friend_list[0]
        friend_two = friend_list[1]
        fb_graph.add_node(friend_one)
        fb_graph.add_node(friend_two)
        fb_graph.add_edge(friend_one, friend_two)
    print(nx.info(fb_graph))
    return fb_graph


def draw_facebook_graph(graph):
    nx.draw(graph)
    plt.savefig("fb.pdf")
    plt.show()


def influence_map(graph, user):
    result = 0
    friends_influence = dict()
    friendmap = number_of_common_friends_map(graph, user)
    for k in friendmap.keys():
        x = common_friends(graph, k, user)
        for cf in x:
            no_of_friends = len(friends(graph, cf))
            result = result + (float(1)/no_of_friends)
        friends_influence[k] = result
        result = 0
    return friends_influence


def recommend_by_influence(graph, user):
    friendmap = influence_map(graph, user)
    return number_map_sorted_list(friendmap)


def evaluate_recommender(graph):
    result = ["Number of friends in common", "Influence"]
    tot_rank_common = float(0)
    tot_rank_influence = float(0)
    num_inf_trials = float(0)
    num_common_trials = float(0)

    for i in range(100):
        friend_1 = random.choice(list(graph.node.keys()))
        friend_2 = random.choice(list(friends(graph, friend_1)))
        graph.remove_edge(friend_1, friend_2)
        rank_inf, num_inf = influence_rank_calc(graph, friend_1, friend_2)
        tot_rank_influence += rank_inf
        num_inf_trials += num_inf
        rank_common, num_common = common_rank_calc(graph, friend_1, friend_2)
        tot_rank_common += rank_common
        num_common_trials += num_common
        graph.add_edge(friend_1, friend_2)

    final_rank_common = tot_rank_common / num_common_trials
    final_rank_influence = tot_rank_influence / num_inf_trials

    print("Average rank of influence method: {} \nAverage rank of number of friends in common method: {}".format(
        final_rank_influence, final_rank_common))
    print("{} method is better".format(
        result[0] if final_rank_common < final_rank_influence else result[1]))


def influence_rank_calc(graph, friend_1, friend_2):
    f2_friends = recommend_by_influence(graph, friend_2)
    f1_friends = recommend_by_influence(graph, friend_1)
    return average_rank_calc(friend_1, friend_2, f1_friends, f2_friends)


def common_rank_calc(graph, friend_1, friend_2):
    f2_friends = recommend_by_number_of_common_friends(graph, friend_2)
    f1_friends = recommend_by_number_of_common_friends(graph, friend_1)
    return average_rank_calc(friend_1, friend_2, f1_friends, f2_friends)


def average_rank_calc(friend_1, friend_2, f1_friends, f2_friends):
    num_trials = float(0)
    average = float(0)

    f1_rank = get_friend_rank(f2_friends, friend_1)
    f2_rank = get_friend_rank(f1_friends, friend_2)
    if f1_rank > 0.0 and f2_rank > 0.0:
        average = (f1_rank+f2_rank)/2.0
        num_trials = num_trials+1.0
    return average, num_trials


def get_friend_rank(friends, friend):
    rank = float(0)
    if friend not in friends:
        return rank
    for f in friends:
        rank += 1
        if f == friend:
            break
    return rank


def diff_algo(graph):
    each_name = set(graph.nodes())
    unchanged = list()
    changed = list()
    for names in each_name:
        recommend_list = recommend_by_influence(graph, names)
        common_list = recommend_by_number_of_common_friends(graph, names)
        if recommend_list == common_list:
            unchanged.append(names)
        else:
            changed.append(name)
    print("unchanged = ", unchanged)
    print("changed = ", changed)


def top_10_common_fb(graph):
    for m in graph:
        n = int(m)
        if n > 1 and n % 1000 == 0:
            all_rec = recommend_by_number_of_common_friends(graph, m)
            top_10_common_rec = all_rec[0:10]
            print("rec for {0} is {1}".format(n, top_10_common_rec))


def top_10_influence_fb(graph):
    for m in graph:
        n = int(m)
        if n > 1 and n % 1000 == 0:
            reco = recommend_by_influence(graph, m)[:10]
            print(n, reco)


def main(argv):
    if(len(argv) == 2):
        fb_file_path = sys.argv[1]
    else:
        sys.exit("Facebook data file path is required..")

    print("\n ************* ROMEO JULIET GRAPH *******************\n")
    rj = create_romeojuliet_graph()

    print("\n **************Comparing two algorithms on romeo juliet graph *************\n")
    diff_algo(rj)
    print("\n******** Computing average rank for the two algorithms on romeo-juliet graph ******")
    evaluate_recommender(rj)

    print("\n********** FACEBOOK GRAPH **************\n")
    fb_graph = create_facebook_graph(file_path)

    print("\n********* Recommendation using common friends for some users in FACEBOOK GRAPH ********\n")
    top_10_common_fb(fb_graph)

    print("\n******** Recommendation using influence algorithm for some users in FACEBOOK GRAPH **********\n")
    top_10_influence_fb(fb_graph)

    print("\n******* Computing average rank for the two algorithms on FACEBOOK GRAPH *******\n")
    evaluate_recommender(fb_graph)

    if __name__ == "__main__":
        main(sys.argv)
