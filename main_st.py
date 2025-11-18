from random import randint
import numpy as np
import streamlit as st
import pandas as pd
from streamlit import session_state
import tags
import functions
from tags import vis_tags, play_tags


min_yr_base=2010
max_yr_base=2025
if "yr_from" not in st.session_state.keys():
    min_yr = 2010 # pd.to_datetime(data_df["releaseDate"]).dt.year.min()
else:
    min_yr = st.session_state["yr_from"]

if "yr_to" not in st.session_state.keys():
    max_yr = 2025
else:
    max_yr = st.session_state["yr_to"]

data_df = pd.read_csv("files/steam_show_df.csv")
yrs_li = [str(i) for i in range(int(min_yr_base),int(max_yr_base)+1)]
rating_li = ['Overwhelmingly Positive', 'Very Positive', 'Positive', 'Mostly Positive', 'Mixed',
                       'Mostly Negative', 'Negative', 'Very Negative', 'Include All']

# global vars
selected_filters = {"yrFrom": min_yr, "yrTo":max_yr, "inclTags":[], "exclTags":["Free to Play"],
                    "minReviews":20, "sales_per_review":35}
#st.session_state = {"yrFrom": min_yr, "yrTo":max_yr, "inclTags":["Casual", "Strategy"], "exclTags":["RPG", "Action"], "min_reviews":1000}


genre_tags = tags.top_genres #["RPG", "Adventure", "Action", "Casual", "Strategy", "Simulation", "Sports", "Racing", "Sandbox", "Visual Novel", "Puzzle", "Platformer", "Shooter", "Roguelike"]
subgenre_tags = tags.sub_genres #["Action RPG", "Action-Adventure", "JRPG", "Roguelike", "Strategy RPG", "Turn-Based Strategy", "Puzzle", "Action Roguelike", "Visual Novel", "Party-Based RPG", "Sandbox", "Shooter", "Interactive Fiction", "Arcade", "Dating Sim", "Platformer", "Card Game", "Life Sim", "Point & Click", "MMORPG", "RTS", "Beat 'em up", "Tower Defense", "Farming Sim", "Auto Battler", "Walking Simulator", "Board Game", "Tabletop", "City Builder", "3D Fighter", "2D Fighter", "Education", "Grand Strategy", "Colony Sim", "Space Sim", "Word Game", "Battle Royale", "Rhythm", "God Game", "4X", "MOBA", "Automobile Sim", "eSports", "Animation & Modeling", "Design & Illustration", "Trivia", "Utilities", "Audio Production", "Video Production", "Photo Editing", "Web Publishing"]
feature_tags = tags.feature_tags
theme_tags = tags.theme_tags
vis_tags = tags.vis_tags
#play_tags = tags.play_tags

incl_tags = []
excl_tags=[]
for key in st.session_state.keys():
    if key.startswith("tag_") and st.session_state[key]:
        incl_tags.append(key.replace("tag_","").replace("_"," "))
    if key.startswith("excl_") and st.session_state[key]:
        excl_tags.append(key.replace("excl_","").replace("_"," "))

# Solely to initialise tags with first use
if 'tagsClicked' not in st.session_state:
    incl_tags = [genre_tags[randint(0,len(genre_tags)-1)] , theme_tags[randint(0,len(theme_tags)-1)]]
    selected_filters["inclTags"] = incl_tags
    excl_tags = ["Free to Play"]
    selected_filters["exclTags"] = excl_tags
    st.session_state['tagsClicked'] = True

filtered_df = functions.filter_data(df=data_df, fallbck=selected_filters, incl_tags=incl_tags, excl_tags=excl_tags)

# STREAMLIT PAGE Preparation

with open('./files/checker.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

st.set_page_config(layout="wide")


### Functions
def on_yr_from():
    if session_state["yr_from"] > session_state["yr_to"]:
        session_state["yr_to"] = session_state["yr_from"]

def on_yr_to():
    if session_state["yr_to"] < session_state["yr_from"]:
        session_state["yr_from"] = session_state["yr_to"]
def count_revenue():
    pass


# STREAMLIT PAGE Creation

with st.container():

    st.subheader("Steam Tag Checker", divider=False)

    ## Selected filters bar
    with st.container(key="filterContainer"):
        st.markdown("SELECTED FILTERS")

        col1, col2, col3, col4 = st.columns([2,2,2,3])
        with col1:
            #st.markdown("**Release Date**")
            st.selectbox("RELEASE DATE FROM:", yrs_li, key="yr_from", on_change=on_yr_from)
            st.selectbox(label="TO:", options=yrs_li, index=len(yrs_li)-1 , key="yr_to", on_change=on_yr_to)

        with col2:
            st.number_input("MINIMUM NO. OF REVIEWS:", step=50, key="min_reviews", min_value=0, value=selected_filters["minReviews"])
            st.selectbox("USER RATINGS FROM:", rating_li, key="min_rating", index=len(rating_li)-1)



            #st.number_input(label="Reviews per sale", label_visibility="visible", step=10, key="rev_per_sale", min_value=1, value=60)

        with col4:
            st.text("REQUIRED TAGS:")
            #st.text(', '.join(s for s in selected_filters["inclTags"]))
            incl_text = ""
            for tag in incl_tags:
                    incl_text += ":violet-badge[:material/check: " + tag + "]"
            st.markdown(incl_text)
            st.text("EXCLUDED TAGS:")
            #st.text(', '.join(s for s in selected_filters["exclTags"]))
            excl_text = ""
            for tag in excl_tags:
                excl_text += ":gray-badge[:material/block: " + tag + "]"
            st.markdown(excl_text)

        with col3:
            st.radio(label="ESTIMATE SALES WITH:", options=[ "Reviews"], index=0, horizontal=True, #options=["Algorithm", "Reviews"], index=1, horizontal=True,
                     key="method_check", on_change=count_revenue())
            if "method_check" in st.session_state.keys() and st.session_state["method_check"] == "Reviews":
                with st.container(border=None, key="condContainer"):
                    colA, colB = st.columns(2)
                    with colA:
                        st.number_input(label="", label_visibility="collapsed", step=1,
                                        key="sales_per_review",
                                        min_value=1, value=selected_filters["sales_per_review"])
                    with colB:
                        st.text("Sales per 1 review")

        ## GAMES SELECTED TEXT
        with st.container(key="selectedContainer"):
            st.text("SELECTED: " + str(filtered_df["game_id"].count()) + " GAMES")


    # TAG SELECTION TABS
    with st.container():
        with st.expander("SELECT TAGS"):
            st.text("TOP GENRES")
            genreCols = st.columns(7)
            for num, col in enumerate(genreCols):
                for i in range(num, len(genre_tags), len(genreCols)):
                    try:
                        val = genre_tags[i] in incl_tags
                        col.checkbox(label=genre_tags[i], key="tag_"+genre_tags[i].replace(" ","_"), value = val)
                    except IndexError:
                        pass
            st.text("SUB-GENRES")
            functions.make_tag_cols(no_of_cols=6, tag_list=subgenre_tags, incl_tags=incl_tags)

            st.text("FEATURES")
            functions.make_tag_cols(no_of_cols=6, tag_list=feature_tags, incl_tags=incl_tags)

            st.text("THEMES")
            functions.make_tag_cols(no_of_cols=6, tag_list=theme_tags, incl_tags=incl_tags)

            st.text("VISUALS")
            functions.make_tag_cols(no_of_cols=6, tag_list=vis_tags, incl_tags=incl_tags)

            st.text("GAMEPLAY")
            functions.make_tag_cols(no_of_cols=6, tag_list=play_tags, incl_tags=incl_tags)

            st.text("OTHER")
            other_tags = functions.find_other_tags(data=data_df, taglist=genre_tags+subgenre_tags+feature_tags+theme_tags+vis_tags+play_tags)
            functions.make_tag_cols(no_of_cols=6, tag_list=other_tags, incl_tags=incl_tags)

        with st.expander("EXCLUDE TAGS"):
            st.text("TOP GENRES")
            genreCols = st.columns(7)
            for num, col in enumerate(genreCols):
                for i in range(num, len(genre_tags), len(genreCols)):
                    try:
                        val = genre_tags[i] in excl_tags
                        col.checkbox(label=genre_tags[i], key="excl_"+genre_tags[i].replace(" ","_"), value = val)
                    except IndexError:
                        pass
            st.text("SUB-GENRES")
            functions.make_extag_cols(no_of_cols=6, tag_list=subgenre_tags, excl_tags=excl_tags)

            st.text("FEATURES")
            functions.make_extag_cols(no_of_cols=6, tag_list=feature_tags, excl_tags=excl_tags)

            st.text("THEMES")
            functions.make_extag_cols(no_of_cols=6, tag_list=theme_tags, excl_tags=excl_tags)

            st.text("VISUALS")
            functions.make_extag_cols(no_of_cols=6, tag_list=vis_tags, excl_tags=excl_tags)

            st.text("GAMEPLAY")
            functions.make_extag_cols(no_of_cols=6, tag_list=play_tags, excl_tags=excl_tags)

            st.text("OTHER")
            functions.make_extag_cols(no_of_cols=6, tag_list=other_tags, excl_tags=excl_tags)

# TABS
    tab1, tab2, tab3, tab4 = st.tabs(["REVENUE", "YEARS", "GAMES LIST", "METHOD"])

    noNaRev_df = filtered_df.dropna(subset="revenue_est")
    noNaRev_count = len(noNaRev_df["revenue_est"])

    with tab1:

        # REVENUE DISTRIBUTION CHARTS
        with st.container(key="sales_info", border=True):
            st.markdown("<p style='text-align: center; font-weight:700; font-size:20px'>Revenue info</p>", unsafe_allow_html=True)
            col_r1, col_r2, col_r3 = st.columns([1,2,1])
            with col_r1:
                if noNaRev_count>1:
                    median = round(noNaRev_df["revenue_est"].median())
                    med_text = f"<p style='font-weight:700'>Median:</p> <p>$ {median}</p>"
                    st.markdown(med_text, unsafe_allow_html=True)
            with col_r2:
                if noNaRev_count<5:
                    bulk_text = "<p style='font-style:italic'>Select more games to see"
                elif noNaRev_count<20:
                    percentile_10 = round(np.percentile(noNaRev_df["revenue_est"], 10))
                    percentile_90 = round(np.percentile(noNaRev_df["revenue_est"], 90))
                    bulk_text = (f"<p style='font-weight:700'>The middle 80% of games earn between:</p>"
                                 f"<p>$ {percentile_10:,}   and   $ {percentile_90:,}</p>")
                else:
                    percentile_15 = round(np.percentile(noNaRev_df["revenue_est"], 15))
                    percentile_85 = round(np.percentile(noNaRev_df["revenue_est"], 85))
                    bulk_text = (f"<p style='font-weight:700'>The middle 70% of games earn between:</p>  "
                                 f"<p>$ {percentile_15:,}   and   $ {percentile_85:,}</p>")
                st.markdown(bulk_text, unsafe_allow_html=True)
            with col_r3:
                st.markdown("<p style='margin-bottom:0px; font-style: italic'>Please Note:</p><p> Set broad filters for this information to be meaningful.</p>",
                            unsafe_allow_html=True)


        with st.container(key="chart_sales"):
            st.markdown(
                "<p style='text-align: right; font-weight:400; font-size:14px; color: grey; font-style: italic'>Hover over the charts for more info</p>",
                unsafe_allow_html=True)
            if noNaRev_count>0:
                fig_hist, skew, is_skewed = functions.plot_histogram(filtered_df, "revenue")
                st.plotly_chart(fig_hist, key="hist_chart")
                ##st.text(skew)
                if is_skewed:
                    line = '''Please note: The chart above has a logarithmic x scale for readability.  
                            For comparison, the revenue distribution on a linear scale is shown below.'''
                    st.markdown(line)
                    fig_viol = functions.plot_distribution(filtered_df)
                    st.plotly_chart(fig_viol, key="dist_chart")
                fig_hist2, skew, is_skewed = functions.plot_histogram(filtered_df, "sales")
                st.plotly_chart(fig_hist2, key="hist_chart_sales")

                #fig_hist_sales, skew2, is_skewed2 = functions.plot_histogram_sales(filtered_df)
                #st.plotly_chart(fig_hist_sales, key="hist_chart_sales")

    with tab2:
        st.text("Note: With data gathered mid-2025, the charts on this page do not include the data for 2025 to avoid a false depiction of trends.")

        with st.container(key="chart_releases"):
            fig_yr = functions.plot_releases_per_year(filtered_df,selected_filters)
            st.plotly_chart(fig_yr)

        with st.container(key="chart_rev_yr"):
            fig_rev_yr = functions.plot_rev_per_year(filtered_df, selected_filters)
            st.plotly_chart(fig_rev_yr)


    with tab3:
        st.dataframe(filtered_df, hide_index=True, on_select="ignore", height=550,
                     column_order=("name", "link", "releaseDate", "tags", "review_count", "positive_reviews",
                                   "user_rating", "price_USD", "revenue_est", "copies_sold_est"),
                     column_config={"name": st.column_config.TextColumn(label="Title", pinned=True),
                                    "link": st.column_config.LinkColumn(label="Link", display_text="link"),
                                    "releaseDate": st.column_config.DateColumn(label="Release Date", format="YYYY-MM"),
                                    "tags": st.column_config.TextColumn(label="Tags", help="Double click to see all tags"),
                                    "review_count": st.column_config.NumberColumn(label="No. of Reviews", format="localized"),
                                    "positive_reviews": st.column_config.NumberColumn(label="Positive", format="percent"),
                                    "user_rating": st.column_config.TextColumn(label="Rating", width="small"),
                                    "price_USD": st.column_config.NumberColumn(label="Price", width="small", format="dollar"),
                                    "revenue_est": st.column_config.NumberColumn(label="Revenue Estimate", format="dollar", step=1),
                                    "copies_sold_est": st.column_config.NumberColumn(label="Copies Sold Est.", format="localized")})

    with tab4:
        st.write("HOW TO USE:\n\n"
                 "- Click on the 'Select tags' button and tick all the tags you want the games to have. NOTE: Only games that have ALL of the selected tags will appear for you.\n\n"
                 "(Yes, the list of tags is ridiculously huge. This is how Steam tags games.)\n\n"
                 "- If you want to exclude games with certain tags, repeat the steps above for the 'Excluded tags' - game with these tags will be removed from the lists and chart calculations.\n\n"
                 "- Apply additional filters using the 'Selected Filters' form at the top of the page.\n\n"
                 "- The 'Games List' tab now contains a list of all Steam games that match your filters\n\n"
                 "- the 'Revenue' and 'Years' tabs contain stats for your selected games' list. Read the data you need from those tabs\n\n"
                 "\n\nINFO:\n\n"
                 "- Games data was gathered from steam in July 2025 with python. You can find the code here https://github.com/out-of-focus/SteamScraping and here: https://github.com/out-of-focus/SteamGamePing\n\n"
                 "- The data was cleaned and in the process I made sure to leave only games available on the Steam store at that time. Playtests, bundles"
                 " etc. were excluded. You can see code for data cleaning (and merging the 2 datasets gotten from steam with 2 different methods) here: https://drive.google.com/file/d/1Qc6KDD_nUEan7852aOu-No1aybsdnOtX/view?usp=sharing \n\n"
                 "- Free to Play games are in the database and you can scroll through them, but they are not included in "
                 "any revenue calculations and charts. \n\n"
                 "- For the time being you can estimate sales and revenue based on the number of reviews only. It's not an exact method, but it has been here for a long time and serves its purpose. "
                 "(I might add a more precise algorithm predicting sales in the future if I find the time and if there's a need for it.)\n\n"
                 "- Want to see the whole industry? Select no tags (remove them from required)\n\n"
                 "Good luck with your games! - Mulak")
#st.write(st.session_state)
