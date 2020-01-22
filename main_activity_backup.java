package com.example.soccerwin365;


import android.app.DatePickerDialog;
import android.app.DialogFragment;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.os.AsyncTask;
import android.os.Handler;
import android.os.Message;
import android.provider.SyncStateContract;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.DatePicker;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.sql.Timestamp;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;


public class MainActivity extends AppCompatActivity implements DatePickerDialog.OnDateSetListener {
    String SelectedDate;
    private String SelectedLeague;
    Long pickedDate;
    SharedPreferences.Editor editor;
    SimpleDateFormat dateFormatter = new SimpleDateFormat("yyyy-MM-dd");
    final DatabaseHelper mDatabaseHelper=new DatabaseHelper(this);
    ArrayList<Game> gameList=new ArrayList<Game>();
    RecyclerView recyclerView;
    MyRecyclerViewAdapter adapter;
    TextView errorView;
    static LinearLayoutManager layoutManager;
    final String URL_Games = "https://eeceboook.000webhostapp.com/soccerwin365/Get.php";
    TextView dateView;
    SharedPreferences pref;
    int PrevRecyclerPosition=0;

    Handler handler=new Handler(){
        @Override
        public void handleMessage(Message msg) {
            showData("Date='" + SelectedDate + "'",true);
            editor.putLong("SelectedDate", pickedDate);
            editor.apply();
        }
    };




    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_activity_action_bar,menu);
        return super.onCreateOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()){
            case R.id.favorit_bar:
                Intent favorit=new Intent(this,Favorit.class);
                startActivity(favorit);
                break;
            case R.id.calendar_bar:
                DatePickerFragement datePicker = new DatePickerFragement();
                datePicker.show(getSupportFragmentManager(),"Date Picker");
                break;


        }


        return super.onOptionsItemSelected(item);
    }



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        getSupportActionBar().setDisplayShowTitleEnabled(false);


        //Set the date
        Date today=new Date();
        pickedDate=today.getTime();
        String TODAY=dateFormatter.format(today);
        SelectedDate=dateFormatter.format(today);

        pref = getSharedPreferences("MyPref", MODE_PRIVATE);
        editor = pref.edit();
        editor.putLong("SelectedDate", pickedDate);
        editor.apply();

        dateView =findViewById(R.id.DateView);
        dateView.setText(SelectedDate);

        ImageView dateBefore=findViewById(R.id.DateBefore);
        dateBefore.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Runnable runnable=new Runnable() {
                    @Override
                    public void run() {
                        pickedDate=pickedDate-24*60*60*1000;
                        SelectedDate=dateFormatter.format(new Date(pickedDate));
                        handler.sendEmptyMessage(0);
                    }

                };

                Thread dateThread=new Thread(runnable);
                dateThread.start();
            }
        });

        ImageView dateAfter=(ImageView) findViewById(R.id.DateAfter);
        dateAfter.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Runnable runnable=new Runnable() {
                    @Override
                    public void run() {
                        pickedDate=pickedDate+24*60*60*1000;
                        SelectedDate=dateFormatter.format(new Date(pickedDate));
                        handler.sendEmptyMessage(0);
                    }

                };

                Thread dateThread=new Thread(runnable);
                dateThread.start();
            }
        });



        SelectedLeague="%";

        recyclerView=findViewById(R.id.theRecycler);
        errorView=(TextView) findViewById(R.id.offline_view);
        //check for connection
        if(NetworkUtils.isConnected(MainActivity.this)){
            loadGames();
            showData("Date='"+SelectedDate+"'",true);
        }else{
            errorView.setVisibility(View.VISIBLE);
            showData("Date='"+SelectedDate+"'",true);
            recyclerView.setOnFlingListener(new RecyclerView.OnFlingListener() {
                @Override
                public boolean onFling(int velocityX, int velocityY) {
                    if(NetworkUtils.isConnected(MainActivity.this)){
                        loadGames();
                        showData("Date='"+SelectedDate+"'",true);

                    }
                    return false;
                }
            });


        }
    }

    @Override
    protected void onPause() {
        PrevRecyclerPosition =layoutManager.findFirstVisibleItemPosition();
        super.onPause();
    }

    @Override
    protected void onResume() {
        //showData("Date='"+SelectedDate+"'"+" and "+"League like'"+SelectedLeague+"'",false);
        //layoutManager.scrollToPosition(PrevRecyclerPosition);
        adapter.notifyDataSetChanged();
        super.onResume();
    }

    private  void loadGames() {
        recyclerView.setOnFlingListener(null);
        errorView.setBackgroundColor(getColor(R.color.BackOnline));
        errorView.setTextColor(getColor(R.color.White));
        errorView.setText(R.string.online);
        gameList=new ArrayList<Game>();
        StringRequest stringRequest = new StringRequest(Request.Method.GET, URL_Games,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        errorView.setVisibility(View.GONE);
                        mDatabaseHelper.deleteData("delete  from "+DatabaseHelper.MATCHES_TABLE_NAME);
                        try {
                            JSONArray array = new JSONArray(response);
                            for (int i = 0; i < array.length(); i++) {
                                JSONObject game = array.getJSONObject(i);
                                mDatabaseHelper.insertMatch(new Game(
                                        game.getInt("id"),
                                        game.getString("home"),
                                        game.getString("away"),
                                        game.getInt("score"),
                                        game.getString("date"),
                                        game.getString("time"),
                                        game.getString("league"),
                                        game.getInt("HId"),
                                        game.getInt("AId"),
                                        R.drawable.star_empty
                                ),DatabaseHelper.MATCHES_TABLE_NAME);
                            }
                            array=null;
                            mDatabaseHelper.close();
                            showData("Date='"+SelectedDate+"'",true);
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {

                    }
                });

        RequestQueue queue=Volley.newRequestQueue(this);
        queue.add(stringRequest);

    }

    public void showData(String condition,boolean changeLeague){
        dateView.setText(SelectedDate);
        Cursor matches=mDatabaseHelper.Select("select * from "+DatabaseHelper.MATCHES_TABLE_NAME+" where "+condition);
        gameList=new ArrayList<Game>();
        List<String> leaguesList=new ArrayList<String>();
        leaguesList.add("All");
        String leag="";
        int favorit;

        //get data from database
        while (matches.moveToNext()) {
            String curruntLeague=matches.getString(6);
            if(!curruntLeague.equals(leag)){
                leaguesList.add(curruntLeague);
                leag=curruntLeague;
            }

            Cursor match=mDatabaseHelper.Select("select Id from "+DatabaseHelper.FAVORITES_TABLE_NAME+" where Id="+matches.getInt(0));
            if(match.moveToFirst()){
                favorit=R.drawable.star_full;
            }else{
                favorit=R.drawable.star_empty;
            }
            gameList.add(new Game(
                    matches.getInt(0),
                    matches.getString(1),
                    matches.getString(2),
                    matches.getInt(3),
                    matches.getString(4),
                    matches.getString(5),
                    matches.getString(6),
                    matches.getInt(7),
                    matches.getInt(8),
                    favorit
            ));
            match.close();
        }

        //Leagues Adapter
        if(changeLeague) {
            RecyclerView LeaguesrecyclerView = findViewById(R.id.LeaguesList);
            LinearLayoutManager horizontalLayoutManager =(LinearLayoutManager) new LinearLayoutManager(MainActivity.this, LinearLayoutManager.HORIZONTAL, false);
            LeaguesrecyclerView.setLayoutManager(horizontalLayoutManager);
            LeaguesrecyclerView.setNestedScrollingEnabled(false);
            LeaguesAdapter leaguesAdapter = new LeaguesAdapter(leaguesList, new LeaguesAdapter.OnItemClickListener() {
                @Override
                public void onItemClick(String item) {
                    String it=item;
                    if(item=="All"){
                        it="%";
                    }
                    SelectedLeague=it;
                    showData("League like '" + it + "'"+" and "+"Date='"+SelectedDate+"'",false);

                }
            });
            LeaguesrecyclerView.setAdapter(leaguesAdapter);
        }
        leaguesList=null;

        
        //Matches Adapter
        layoutManager = (LinearLayoutManager) new LinearLayoutManager(MainActivity.this);
        recyclerView.setLayoutManager(layoutManager);
        recyclerView.setNestedScrollingEnabled(false);
        adapter =new MyRecyclerViewAdapter(gameList, new MyRecyclerViewAdapter.OnItemClickListener() {
            @Override
            public void onItemClick(Game item) {

                if(item.mFavorit==R.drawable.star_empty){
                    mDatabaseHelper.insertMatch(item,DatabaseHelper.FAVORITES_TABLE_NAME);
                }else{
                    mDatabaseHelper.deleteData("delete from "+mDatabaseHelper.FAVORITES_TABLE_NAME+" where Id="+item.mId);

                }
                item.switchFavorit();
            }
        });
        recyclerView.setAdapter(adapter);
        gameList=null;
        matches.close();
        mDatabaseHelper.close();
        
        
    }

    @Override
    public void onDateSet(DatePicker view, int year, int month, int dayOfMonth) {

        Calendar c=Calendar.getInstance();
        c.set(year,month,dayOfMonth);

        pickedDate=c.getTimeInMillis();
        editor.putLong("SelectedDate",pickedDate );
        editor.apply();
        SelectedDate=dateFormatter.format(pickedDate);
        showData("Date='" + SelectedDate + "'",true);
    }

}